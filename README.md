# hungyi-tw.net

余竑毅的個人學術網站，中英雙語。純 HTML/CSS，沒有建置步驟，部署在 Cloudflare Pages。

## 目錄結構

```
.
├── public/                 ← Cloudflare Pages 的輸出目錄（整個網站）
│   ├── index.html          首頁
│   ├── research/           研究
│   ├── publications/       論文
│   ├── teaching/           教學
│   ├── dev/                開發
│   ├── notes/              筆記（結構已備好，尚未開放、noindex）
│   ├── assets/
│   │   ├── css/tokens.css  design system 的 token（顏色、字級、間距）
│   │   ├── css/site.css    版面與元件
│   │   └── js/site.js      語言切換、主題切換、進場過場（非必要，關掉仍完整可讀）
│   ├── _headers            安全標頭與快取規則
│   ├── _redirects          轉址規則
│   ├── robots.txt
│   ├── sitemap.xml
│   └── favicon.svg
├── functions/              ← 之後要加動態功能的地方（見 functions/README.md）
├── tools/build_pages.py    ← 選用：重新產生所有頁面的腳本
└── wrangler.toml
```

## 改內容

直接編輯 `public/` 底下的 `.html` 檔即可，存檔後用瀏覽器打開就能看。
共用區塊（導覽列、頁尾、信箱）改 `tools/build_pages.py` 後重新產生。

改樣式一律改 `assets/css/tokens.css` 的變數，不要在 `site.css` 裡寫死顏色或尺寸——
這樣深色主題才會跟著一起正確。

> **關於 `tools/build_pages.py`**
> 導覽列、頁尾、信箱這些東西在六個 HTML 檔裡是重複的。要改這類共用區塊時，
> 改腳本再跑一次 `python3 tools/build_pages.py` 比手動改六個檔案安全。
> 但這不是建置步驟：產出的 HTML 已經在 repo 裡，沒有 Python 也能正常部署。

## 部署

### 方法一：直接上傳（現在就能用，不需要 GitHub）

1. 把 `public/` 資料夾壓成 zip
2. Cloudflare Dashboard → Workers & Pages → Create → Pages → Upload assets
3. 專案名稱填 `hungyi-tw`，上傳 zip
4. 專案建好後 → Custom domains → Set up a custom domain → 填 `hungyi-tw.net`
   （網域已經在同一個 Cloudflare 帳號，DNS 會自動設好，apex 網域由 CNAME flattening 處理）
5. 同一頁再加一個 `www.hungyi-tw.net` 並設成轉址到主網域（選用）

### 方法二：接 GitHub 自動部署（之後要開的時候）

1. `git init && git add -A && git commit -m "init"`，推到一個新的 GitHub repo
2. Cloudflare Dashboard → Workers & Pages → Create → Pages → Connect to Git
3. 設定：
   - Framework preset：**None**
   - Build command：**留空**
   - Build output directory：**`public`**
4. 之後每次 push 到 main 就會自動部署，PR 會有預覽網址

`wrangler.toml` 已經寫好 `pages_build_output_dir`，所以用 `wrangler pages deploy`
從指令列部署也可以：

```bash
npx wrangler pages deploy
```

## 本機預覽

純靜態預覽：

```bash
python3 -m http.server 8000 --directory public
```

要同時測 `functions/` 的動態端點：

```bash
npx wrangler pages dev public
```

## 免費額度

靜態檔案的請求與流量免費且無上限。有數字的限制是：每月 500 次建置、
同時 1 個建置、單次建置 20 分鐘、單一專案 20,000 個檔案、單檔 25 MiB。
`functions/` 的動態請求算 Workers，免費為每天 100,000 次、每次 10ms CPU。
這個網站目前不會用到動態額度。

## 待辦

- [ ] 換掉所有 `TODO:` 標記的佔位內容
- [ ] 放上 `public/cv.pdf`
- [ ] 換掉 `tools/build_pages.py` 裡的信箱、ORCID、Google Scholar、GitHub 連結後重新產生
- [ ] 首頁 Hero 決定要顯示中文全名還是 Ian
- [ ] 需要時開啟 Notes（步驟寫在 `public/notes/index.html` 的註解裡）
