# Outreach next actions

2026-07-02 時点の営業メール改善アクション。

## 実施方針

- 大量再送はしない。まず10件だけ短文追客する。
- 追客メールは「打ち合わせ予約」ではなく「実データ版を1枚作ってよいか」のYes/Noにする。
- URLにはUTMを付与し、少なくともキャンペーン別・宛先別に識別できる状態にする。
- 宛先CSV、送信ログ、送信者情報は `data/.gitignore` の対象として公開しない。

## 追客バッチ生成

```sh
python3 scripts/build_followup_batch.py --limit 10 --campaign followup_20260702
```

生成物:

- `data/followup_20260702.csv`

送信前プレビュー:

```sh
python3 scripts/send_outreach.py \
  --recipients data/followup_20260702.csv \
  --subject-template config/outreach/followup_subject.txt \
  --body-template config/outreach/followup_body.txt \
  --campaign followup_20260702
```

送信:

```sh
SMTP_HOST=mail1044.onamae.ne.jp SMTP_PORT=587 SMTP_MODE=starttls SMTP_USER=support@koetech.jp SMTP_PASS=... \
python3 scripts/send_outreach.py \
  --send --resend --sleep 20 \
  --recipients data/followup_20260702.csv \
  --subject-template config/outreach/followup_subject.txt \
  --body-template config/outreach/followup_body.txt \
  --campaign followup_20260702
```

## DNS到達性

現在確認済み:

- SPF: `v=spf1 include:_spf.onamae.ne.jp ~all`
- MX: `10 mail1044.onamae.ne.jp.`
- DKIM: `default._domainkey.koetech.jp` に `v=DKIM1; k=rsa; p=...` が存在
- DMARC: 未設定

DNSに追加する推奨レコード:

```txt
_dmarc.koetech.jp. TXT "v=DMARC1; p=none; rua=mailto:support@koetech.jp; fo=1; adkim=r; aspf=r"
```

DMARCはまず `p=none` で集計し、到達状況を見てから `quarantine` 以上を検討する。
