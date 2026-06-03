# RemoteCareer AI Blog
Hugo + GitHub Actions + Cloudflare Pages による完全自動ブログ

## セットアップ手順（30分で完成）

### 1. リポジトリを GitHub に push
```bash
git init
git add .
git commit -m "initial setup"
git remote add origin https://github.com/YOUR_NAME/remote-career-blog.git
git push -u origin main
```

### 2. GitHub Secrets を設定
リポジトリの Settings → Secrets → Actions に追加：
- `ANTHROPIC_API_KEY` ← Anthropic Console から取得

### 3. Cloudflare Pages に接続
1. Cloudflare ダッシュボード → Workers & Pages → Create application
2. Connect to Git → GitHub リポジトリを選択
3. Build settings:
   - Framework preset: **Hugo**
   - Build command: `hugo`
   - Build output directory: `public`
4. Save and Deploy

### 4. 動作確認
GitHub Actions タブ → Daily Auto Post → Run workflow で手動実行

---

## ファイル構成
```
remote-career-blog/
├── .github/
│   └── workflows/
│       └── daily-post.yml     # 毎日 06:00 UTC に自動実行
├── content/
│   └── posts/                 # AI が生成した記事（.md）が入る
├── layouts/
│   └── _default/
│       ├── baseof.html        # SEO・OGP・構造化データ
│       ├── single.html        # 記事ページ
│       └── list.html          # 一覧ページ
├── scripts/
│   └── generate_post.py      # Batch API で記事生成
└── hugo.toml                  # サイト設定
```

## コスト（月30記事の場合）
| 項目 | 月額 |
|------|------|
| Anthropic Batch API | ~$0.17 |
| Cloudflare Pages | 無料 |
| GitHub Actions | 無料 |
| **合計** | **~$0.17** |
