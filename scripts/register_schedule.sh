#!/bin/bash
# 平日14-17時 自動送信スケジュール(LaunchAgent)をOSに登録する。
# ユーザーが手動で実行する想定:  bash scripts/register_schedule.sh
set -uo pipefail

SRC="/Users/ryutarote/Developer/web-renewal-studio/config/launchd/com.koetech.outreach.plist"
DST="$HOME/Library/LaunchAgents/com.koetech.outreach.plist"
UID_NUM="$(id -u)"
LABEL="com.koetech.outreach"

mkdir -p "$HOME/Library/LaunchAgents"
cp "$SRC" "$DST"
echo "plist copied -> $DST"

# 既存があれば一旦解除（無ければ無視）
launchctl bootout "gui/${UID_NUM}/${LABEL}" 2>/dev/null || true

# 登録
if launchctl bootstrap "gui/${UID_NUM}" "$DST"; then
  echo "bootstrap OK"
else
  echo "bootstrap がエラー（既に登録済みの可能性）。状態を確認します。"
fi
launchctl enable "gui/${UID_NUM}/${LABEL}" 2>/dev/null || true

echo "----- 登録状態 -----"
launchctl print "gui/${UID_NUM}/${LABEL}" 2>/dev/null | grep -iE "state|program|next" | head
echo "--------------------"
echo "state = waiting / running なら登録成功＝平日14-17時スケジュール稼働。"
