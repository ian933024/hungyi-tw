# functions/ — 之後要加動態功能的地方

目前只有一個 `api/ping.js` 當作佔位與健康檢查。網站現在是 100% 靜態，
不會消耗任何 Workers 額度。

## 之後可能會放進來的東西

| 想做的事 | 檔案 | 額外需要 |
| --- | --- | --- |
| 聯絡表單（收信） | `functions/api/contact.js` | 一個寄信服務的 API key，存成 Pages 的環境變數 |
| 訪客／論文下載計數 | `functions/api/hit.js` | Cloudflare KV 或 D1 綁定 |
| 論文清單改成資料驅動 | `functions/api/publications.js` | D1，或直接讀一份 JSON |
| 擋爬蟲的信箱解碼 | `functions/api/mail.js` | 無 |

## 路徑規則

```
functions/api/ping.js      →  /api/ping
functions/api/[slug].js    →  /api/:slug
functions/_middleware.js   →  所有路徑的前置處理
```

## 本機測試

```bash
npx wrangler pages dev public
```

`wrangler.toml` 已經設好 `pages_build_output_dir = "public"`，所以綁定
（KV、D1、環境變數）之後也寫在那個檔案裡，本機與線上會一致。
