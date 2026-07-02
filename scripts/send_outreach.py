#!/usr/bin/env python3
"""
営業メール送信スクリプト（リニューアル提案デモの案内）。

安全のため **既定は dry-run**（実送信しない）。実送信は --send を明示した時だけ。

  # 1) プレビュー（送信しない・data/outreach_preview/ に .eml を書き出す）
  python3 scripts/send_outreach.py

  # 2) 1件だけ自分宛にテスト送信
  SMTP_HOST=... SMTP_PORT=587 SMTP_USER=... SMTP_PASS=... \
      python3 scripts/send_outreach.py --send --only udonbakaichidai \
      --override-to you@example.com

  # 3) 本送信（宛先メールが埋まった行のみ・スロットリング＆送信ログでresume）
  SMTP_HOST=... SMTP_PORT=587 SMTP_USER=... SMTP_PASS=... \
      python3 scripts/send_outreach.py --send

入力:
  data/recipients.csv          … 宛先（build_recipients.py で生成、email列を手入力）
  data/outreach_sender.json    … 送信者情報（config/outreach/sender.example.json を複製）
  config/outreach/subject.txt  … 件名テンプレ
  config/outreach/body.txt     … 本文テンプレ
SMTP 認証情報は環境変数で渡す（ファイルに書かない）:
  SMTP_HOST, SMTP_PORT(=587), SMTP_USER, SMTP_PASS,
  SMTP_MODE(=starttls|ssl|plain, 既定 starttls)
送信ログ:
  data/sent_log.csv … 送信済みslugを記録。再実行で重複送信しない（--resend で無視）。
"""
import argparse
import csv
import json
import os
import re
import smtplib
import ssl
import sys
import time
from email.headerregistry import Address
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECIPIENTS = os.path.join(ROOT, "data", "recipients.csv")
SENDER_CFG = os.path.join(ROOT, "data", "outreach_sender.json")
SUBJECT_TPL = os.path.join(ROOT, "config", "outreach", "subject.txt")
BODY_TPL = os.path.join(ROOT, "config", "outreach", "body.txt")
PREVIEW_DIR = os.path.join(ROOT, "data", "outreach_preview")
SENT_LOG = os.path.join(ROOT, "data", "sent_log.csv")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def render(tpl: str, ctx: dict) -> str:
    out = tpl
    for k, v in ctx.items():
        out = out.replace("{{" + k + "}}", str(v))
    leftover = re.findall(r"\{\{(\w+)\}\}", out)
    if leftover:
        die(f"テンプレに未解決のプレースホルダ: {sorted(set(leftover))}")
    return out


def load_sender():
    if not os.path.exists(SENDER_CFG):
        die(
            f"送信者情報がありません: {SENDER_CFG}\n"
            f"  cp config/outreach/sender.example.json {SENDER_CFG} して自社情報を記入してください。"
        )
    with open(SENDER_CFG, encoding="utf-8") as f:
        cfg = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
    required = ["sender_name", "sender_company", "sender_address", "sender_email"]
    missing = [k for k in required if not str(cfg.get(k, "")).strip()
               or str(cfg[k]).startswith("（")]
    if missing:
        die(f"data/outreach_sender.json の未記入項目: {missing}")
    cfg.setdefault("sender_phone", "")
    if not str(cfg.get("optout", "")).strip() or str(cfg["optout"]).startswith("（"):
        cfg["optout"] = cfg["sender_email"]
    cfg.setdefault("top_url", "https://ryutarote.github.io/web-renewal-studio/")
    if not EMAIL_RE.match(cfg["sender_email"]):
        die(f"sender_email が不正: {cfg['sender_email']}")
    return cfg


def load_rows():
    if not os.path.exists(RECIPIENTS):
        die(f"{RECIPIENTS} がありません。先に build_recipients.py を実行してください。")
    with open(RECIPIENTS, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_sent():
    sent = set()
    if os.path.exists(SENT_LOG):
        with open(SENT_LOG, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("status") == "sent":
                    sent.add(r["slug"])
    return sent


def append_sent(slug, to_addr, status, detail=""):
    new = not os.path.exists(SENT_LOG)
    with open(SENT_LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts", "slug", "to", "status", "detail"])
        w.writerow([formatdate(localtime=True), slug, to_addr, status, detail])


def build_message(row, sender, subject_tpl, body_tpl, to_addr, campaign=""):
    demo_url = row.get("tracked_demo_url", "").strip() or row.get("demo_url", "").strip()
    ctx = {
        **row,
        "shop_name": row["shop_name"],
        "area_genre": row.get("area_genre", ""),
        "demo_url": demo_url,
        "campaign": campaign,
        **sender,
    }
    subject = render(subject_tpl, ctx).strip()
    body = render(body_tpl, ctx)

    msg = EmailMessage()
    msg["Subject"] = subject
    name, domain = sender["sender_email"].split("@", 1)
    msg["From"] = Address(sender["sender_company"], name, domain)
    msg["To"] = to_addr
    msg["Reply-To"] = sender["sender_email"]
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=domain)
    # ワンクリック配信停止（特定電子メール法の配信停止導線）
    msg["List-Unsubscribe"] = f"<mailto:{sender['optout']}?subject=unsubscribe>"
    msg.set_content(body)
    return msg, subject


def smtp_connect():
    host = os.environ.get("SMTP_HOST")
    if not host:
        die("環境変数 SMTP_HOST が未設定です（SMTP情報を渡してください）。")
    port = int(os.environ.get("SMTP_PORT", "587"))
    mode = os.environ.get("SMTP_MODE", "starttls").lower()
    user = os.environ.get("SMTP_USER")
    pw = os.environ.get("SMTP_PASS")
    if mode == "ssl":
        s = smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=30)
    else:
        s = smtplib.SMTP(host, port, timeout=30)
        s.ehlo()
        if mode == "starttls":
            s.starttls(context=ssl.create_default_context())
            s.ehlo()
    if user and pw:
        s.login(user, pw)
    return s


def main():
    global RECIPIENTS
    ap = argparse.ArgumentParser(description="営業メール送信（既定はdry-run）")
    ap.add_argument("--send", action="store_true", help="実際に送信する（未指定はdry-run）")
    ap.add_argument("--only", action="append", default=[],
                    help="このslugだけ対象（複数可）")
    ap.add_argument("--limit", type=int, default=0, help="先頭N件だけ処理（0=無制限）")
    ap.add_argument("--sleep", type=float, default=20.0,
                    help="送信間隔秒（既定20s・連投によるブロック回避）")
    ap.add_argument("--override-to", default="",
                    help="全件をこのアドレスへ（送信テスト用）")
    ap.add_argument("--resend", action="store_true", help="送信ログを無視して再送")
    ap.add_argument("--recipients", default=RECIPIENTS,
                    help="宛先CSV（既定 data/recipients.csv）")
    ap.add_argument("--subject-template", default=SUBJECT_TPL,
                    help="件名テンプレート（既定 config/outreach/subject.txt）")
    ap.add_argument("--body-template", default=BODY_TPL,
                    help="本文テンプレート（既定 config/outreach/body.txt）")
    ap.add_argument("--campaign", default="",
                    help="送信ログdetailとテンプレート{{campaign}}に入れる識別子")
    ap.add_argument("--count-targets", action="store_true",
                    help="送信対象件数だけを出力して終了（SMTPには接続しない）")
    args = ap.parse_args()

    sender = load_sender()
    RECIPIENTS = args.recipients
    rows = load_rows()
    with open(args.subject_template, encoding="utf-8") as f:
        subject_tpl = f.read()
    with open(args.body_template, encoding="utf-8") as f:
        body_tpl = f.read()

    if args.only:
        rows = [r for r in rows if r["slug"] in set(args.only)]
    sent = set() if args.resend else load_sent()

    # 対象選別
    targets, skipped = [], []
    for r in rows:
        slug = r["slug"]
        to_addr = args.override_to or r.get("email", "").strip()
        if not to_addr:
            skipped.append((slug, "email空"))
            continue
        if not EMAIL_RE.match(to_addr):
            skipped.append((slug, f"email不正:{to_addr}"))
            continue
        if slug in sent:
            skipped.append((slug, "送信済み(skip)"))
            continue
        targets.append((r, to_addr))

    if args.limit:
        targets = targets[: args.limit]

    if args.count_targets:
        print(len(targets))
        return

    mode = "送信" if args.send else "DRY-RUN（送信しない）"
    print(f"== 営業メール {mode} ==")
    print(f"対象 {len(targets)} 件 / スキップ {len(skipped)} 件 / 全{len(rows)}行")
    if skipped:
        empty = sum(1 for _, why in skipped if why == "email空")
        print(f"  （スキップ内訳: email空={empty}, その他={len(skipped) - empty}）")

    if not args.send:
        os.makedirs(PREVIEW_DIR, exist_ok=True)
        for r, to_addr in targets:
            msg, subject = build_message(r, sender, subject_tpl, body_tpl, to_addr, args.campaign)
            path = os.path.join(PREVIEW_DIR, f"{r['slug']}.eml")
            with open(path, "wb") as f:
                f.write(bytes(msg))
        print(f"プレビュー(.eml)を {PREVIEW_DIR} に書き出しました（{len(targets)}件）。")
        if targets:
            r0, to0 = targets[0]
            m0, subj0 = build_message(r0, sender, subject_tpl, body_tpl, to0, args.campaign)
            print("\n--- サンプル（1通目） ---")
            print(f"To: {to0}\nFrom: {m0['From']}\nSubject: {subj0}\n")
            print(m0.get_content())
        print("\n実送信は  --send  を付けて実行してください。")
        return

    if not targets:
        print("送信対象がありません（emailを data/recipients.csv に入力してください）。")
        return

    print(f"送信間隔: {args.sleep}s。開始します...")
    s = smtp_connect()
    ok = err = 0
    try:
        for i, (r, to_addr) in enumerate(targets, 1):
            msg, subject = build_message(r, sender, subject_tpl, body_tpl, to_addr, args.campaign)
            try:
                s.send_message(msg)
                ok += 1
                append_sent(r["slug"], to_addr, "sent", args.campaign)
                print(f"[{i}/{len(targets)}] OK  {r['slug']} -> {to_addr}")
            except Exception as e:  # noqa: BLE001
                err += 1
                append_sent(r["slug"], to_addr, "error", str(e))
                print(f"[{i}/{len(targets)}] ERR {r['slug']} -> {to_addr}: {e}")
                try:
                    s.noop()
                except Exception:  # 接続切れ → 再接続
                    s = smtp_connect()
            if i < len(targets) and args.sleep > 0:
                time.sleep(args.sleep)
    finally:
        try:
            s.quit()
        except Exception:
            pass
    print(f"\n完了: 成功 {ok} / 失敗 {err}。ログ: {SENT_LOG}")


if __name__ == "__main__":
    main()
