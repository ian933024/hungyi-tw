/**
 * Cloudflare Pages Function — 範例端點
 * 部署後可用 GET https://hungyi-tw.net/api/ping 驗證動態層是否正常。
 *
 * 這個檔案存在的唯一目的是「佔住位置」：它證明 functions/ 目錄有被 Pages 認出來。
 * 之後要加真的動態功能（聯絡表單、訪客計數、API 代理）時，
 * 在 functions/ 底下依路徑新增檔案即可，不需要改任何前端設定。
 *
 * 路徑對應：functions/api/ping.js  →  /api/ping
 *           functions/api/[id].js  →  /api/:id
 *
 * 免費額度：Functions 算 Workers，每天 100,000 次請求、每次 10ms CPU。
 * 純靜態頁面不會用到這個額度。
 */
export function onRequestGet() {
  return new Response(
    JSON.stringify({ ok: true, at: new Date().toISOString() }),
    {
      headers: {
        'content-type': 'application/json; charset=utf-8',
        'cache-control': 'no-store',
      },
    }
  );
}
