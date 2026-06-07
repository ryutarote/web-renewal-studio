#!/usr/bin/env python3
"""#5 トークン体系の統一（第1弾5サイト）。冪等。

第1弾サイトの独自命名(--indigo 等/hex)を、shadcn系のHSLセマンティックトークンを
「唯一の真実」とする構成へ移行。既存コンポーネントは無改修のまま、旧名は同色の
エイリアス（hsl(var(--x))）として残すため、見た目はHSL丸め誤差のみ＝ほぼ不変。
"""
import sys, re, pathlib, colorsys

SITES = pathlib.Path(__file__).resolve().parent.parent / "sites"
FIRST_GEN = ["udonbakaichidai","hiroshima-mitchan","nagasaki-shikairou","morioka-jajamen","utsunomiya-minmin"]
MARK = "統一デザイントークン（shadcn系・HSL／唯一の真実）"

def hex2hsl(h):
    h = h.strip().lstrip("#")
    r,g,b = (int(h[i:i+2],16)/255 for i in (0,2,4))
    hue,l,s = colorsys.rgb_to_hls(r,g,b)
    return f"{round(hue*360)} {round(s*100)}% {round(l*100)}%"

def get(root, name):
    m = re.search(rf"--{re.escape(name)}:\s*([^;]+);", root)
    return m.group(1).strip() if m else None

errors=[]
def process(slug):
    f = SITES/slug/"css"/"style.css"
    s = f.read_text(encoding="utf-8")
    if MARK in s:
        return False
    m = re.search(r":root\s*\{.*?\n\}", s, re.S)
    if not m:
        errors.append(f"{slug}: :root 不在"); return False
    root = m.group(0)
    hexes = {n: get(root, n) for n in
             ["indigo","indigo-dark","gold","gold-deep","cream","paper","vermilion","ink","muted","line"]}
    if any(v is None or not v.startswith("#") for v in hexes.values()):
        errors.append(f"{slug}: hex抽出失敗 {hexes}"); return False
    shadow = get(root,"shadow"); radius = get(root,"radius") or "14px"
    serif = get(root,"serif"); sans = get(root,"sans")
    H = {k: hex2hsl(v) for k,v in hexes.items()}
    new = f""":root {{
  /* ===== {MARK} ===== */
  --background: {H['cream']};
  --foreground: {H['ink']};
  --card: {H['paper']};
  --card-foreground: {H['ink']};
  --primary: {H['indigo']};
  --primary-strong: {H['indigo-dark']};
  --primary-foreground: {H['cream']};
  --secondary: {H['paper']};
  --secondary-foreground: {H['indigo-dark']};
  --muted-foreground: {H['muted']};
  --accent: {H['gold']};
  --accent-strong: {H['gold-deep']};
  --accent-foreground: {H['indigo-dark']};
  --destructive: {H['vermilion']};
  --border: {H['line']};
  --input: {H['line']};
  --ring: {H['gold']};
  --radius: {radius};

  /* ===== 後方互換エイリアス（既存コンポーネントは無改修・同色） =====
     ※旧 --muted はテキスト色のため --muted-foreground を参照（shadcnの背景用--mutedとは別） */
  --indigo: hsl(var(--primary));
  --indigo-dark: hsl(var(--primary-strong));
  --gold: hsl(var(--accent));
  --gold-deep: hsl(var(--accent-strong));
  --cream: hsl(var(--background));
  --paper: hsl(var(--card));
  --vermilion: hsl(var(--destructive));
  --ink: hsl(var(--foreground));
  --muted: hsl(var(--muted-foreground));
  --line: hsl(var(--border));
  --shadow: {shadow};
  --serif: {serif};
  --sans: {sans};
}}"""
    s = s[:m.start()] + new + s[m.end():]
    f.write_text(s, encoding="utf-8")
    return True

def main():
    for slug in FIRST_GEN:
        ch = process(slug)
        print(f"  {slug:22} {'updated' if ch else 'skip/err'}")
    if errors:
        print("\n*** エラー ***");
        for e in errors: print("  -",e)
        sys.exit(1)
    print("\nOK")

if __name__=="__main__":
    main()
