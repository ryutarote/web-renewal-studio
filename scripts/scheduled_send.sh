#!/bin/bash
# 平日14:00〜17:00のみ営業メールを送信するスケジュール実行ラッパー。
# launchd(LaunchAgent: com.koetech.outreach) から平日14/15/16時に起動される。
# 二重送信は send_outreach.py 側の sent_log.csv で防止（同一slugは再送しない）。
#
# SMTPパスワードは平文ファイルに置かず macOS Keychain から取得する。
# 事前に一度だけ（ユーザーが実行）:
#   security add-generic-password -s koetech-smtp -a support@koetech.jp -T /usr/bin/security -w
#   （-w を値なしで付けると、パスワードを画面非表示のプロンプトで入力できる）
set -uo pipefail

REPO="/Users/ryutarote/Developer/web-renewal-studio"
LOG="$REPO/data/scheduled_send.log"
PY="/usr/bin/python3"   # 標準ライブラリのみ使用するため system python で十分
RESEND_ONCE_FLAG="$REPO/data/resend_all_once_at_14.flag"
RESEND_ONCE_DONE="$REPO/data/resend_all_once_at_14.done"

# --- 非機密のSMTP設定（パスワード以外）---
export SMTP_HOST='mail1044.onamae.ne.jp'
export SMTP_PORT='587'
export SMTP_MODE='starttls'
export SMTP_USER='support@koetech.jp'

ts() { date '+%Y-%m-%d %H:%M:%S %a'; }

dow=$(date +%u)   # 1=月 .. 7=日
hour=$(date +%H)  # 00..23

# 平日(1-5) かつ 14<=hour<=16（=14:00-16:59）のみ実行。
# スリープ復帰などで時間外に起動された場合はここで安全に抜ける。
if [ "$dow" -gt 5 ] || [ "$hour" -lt 14 ] || [ "$hour" -gt 16 ]; then
  echo "$(ts) SKIP 時間外/休日 (dow=$dow hour=$hour)" >> "$LOG"
  exit 0
fi

# --- パスワードはKeychainから（平文保存しない）---
SMTP_PASS="$(security find-generic-password -s koetech-smtp -a "$SMTP_USER" -w 2>/dev/null)"
if [ -z "${SMTP_PASS:-}" ]; then
  echo "$(ts) ERROR Keychainにkoetech-smtpが無い。先に security add-generic-password を実行してください" >> "$LOG"
  exit 1
fi
export SMTP_PASS

cd "$REPO" || { echo "$(ts) ERROR cd失敗" >> "$LOG"; exit 1; }

COUNT_ARGS=(--count-targets)
SEND_ARGS=(--send --sleep 20)
resend_once=0
if [ -f "$RESEND_ONCE_FLAG" ] && [ "$hour" -eq 14 ]; then
  COUNT_ARGS+=(--resend)
  SEND_ARGS+=(--resend)
  resend_once=1
  echo "$(ts) INFO 一回限りの全送信フラグを検出。送信済みログを無視して14時に再送します" >> "$LOG"
fi

pending_count="$("$PY" scripts/send_outreach.py "${COUNT_ARGS[@]}" 2>>"$LOG")"
if [ $? -ne 0 ] || ! [[ "$pending_count" =~ ^[0-9]+$ ]]; then
  echo "$(ts) ERROR 送信対象件数の確認に失敗: ${pending_count:-<empty>}" >> "$LOG"
  exit 1
fi
if [ "$pending_count" -eq 0 ]; then
  echo "$(ts) SKIP 未送信メール対象なし" >> "$LOG"
  exit 0
fi

echo "$(ts) RUN send_outreach.py --send (平日午後ウィンドウ)" >> "$LOG"
"$PY" scripts/send_outreach.py "${SEND_ARGS[@]}" >> "$LOG" 2>&1
rc=$?
if [ "$resend_once" -eq 1 ]; then
  mv "$RESEND_ONCE_FLAG" "$RESEND_ONCE_DONE" 2>>"$LOG" || true
fi
echo "$(ts) DONE rc=$rc" >> "$LOG"
