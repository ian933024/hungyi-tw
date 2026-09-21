# -*- coding: utf-8 -*-
"""一次性的頁面產生器：把共用的 header/footer 與各頁內容組成純靜態 HTML。
產出的是純 HTML/CSS，網站本身不需要任何建置步驟。"""
import os, io

SITE = "https://hungyi-tw.net"
UPDATED = "2026.09.21"
MAIL = "ian [at] example.edu"          # TODO: 換成真實信箱寫法
MAIL_HREF = "mailto:ian@example.edu"   # TODO: 換成真實信箱

NAV = [
    ("/research/",     "RESEARCH",     "research"),
    ("/publications/", "PUBLICATIONS", "publications"),
    ("/teaching/",     "TEACHING",     "teaching"),
    ("/dev/",          "DEV",          "dev"),
]

EXT = [
    ("https://orcid.org/0000-0000-0000-0000", "ORCID"),   # TODO
    ("https://scholar.google.com/",           "SCHOLAR"), # TODO
    ("https://github.com/",                   "GITHUB"),  # TODO
]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Newsreader:opsz,wght@6..72,400;6..72,500'
         '&amp;family=Noto+Serif+TC:wght@400;500'
         '&amp;family=IBM+Plex+Sans:wght@400;500;600'
         '&amp;family=IBM+Plex+Sans+TC:wght@400;500;600'
         '&amp;family=IBM+Plex+Mono:wght@400&amp;display=swap">')

THEME_BOOT = """<script>
    /* 在畫面繪製前套用主題，避免切換時閃一下白底 */
    (function () {
      var r = document.documentElement;
      r.classList.remove('no-js');
      try { var t = localStorage.getItem('theme'); if (t === 'light' || t === 'dark') r.setAttribute('data-theme', t); } catch (e) {}
      /* 保險：site.js 若載入失敗，2 秒後仍把所有內容顯示出來 */
      setTimeout(function () { r.classList.add('reveal-fallback'); }, 2000);
    })();
  </script>"""


def head(title, desc, canonical, noindex=False):
    robots = '\n  <meta name="robots" content="noindex, nofollow">' if noindex else ''
    return f"""<!DOCTYPE html>
<html lang="zh-Hant-TW" class="no-js">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">{robots}
  <link rel="canonical" href="{SITE}{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{SITE}{canonical}">
  <meta property="og:locale" content="zh_TW">
  <meta name="theme-color" content="#faf8f4" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#151412" media="(prefers-color-scheme: dark)">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  {FONTS}
  <link rel="stylesheet" href="/assets/css/tokens.css">
  <link rel="stylesheet" href="/assets/css/site.css">
  {THEME_BOOT}
</head>
<body>
  <a class="skip-link body-sm" href="#main">跳到主要內容</a>
"""


def header(active):
    CUR = ' aria-current="page"'
    nav = "\n".join(
        '        <a href="%s"%s>%s</a>' % (href, CUR if key == active else "", label)
        for href, label, key in NAV
    )
    ext = "\n".join(
        f'        <a href="{href}" rel="me noopener" target="_blank">{label}</a>' for href, label in EXT
    )
    return f"""  <header class="site-header">
    <div class="wrap wrap--wide">
      <div class="site-header__bar">
        <a class="site-header__mark" href="/">Ian</a>
        <nav class="site-nav label" aria-label="主要導覽">
{nav}
        </nav>
        <div class="site-header__aside label">
{ext}
          <button class="theme-toggle" type="button" data-theme-toggle>DARK</button>
        </div>
      </div>
    </div>
  </header>

  <main id="main">
"""


FOOTER = f"""  </main>

  <footer class="site-footer">
    <div class="wrap wrap--wide site-footer__inner">
      <div class="site-footer__cols">
        <div>
          <p class="site-footer__label label">CONTACT</p>
          <a class="site-footer__mail" href="{MAIL_HREF}">{MAIL}</a>
        </div>
        <nav class="site-footer__links label" aria-label="外部連結">
""" + "\n".join(
    f'          <a href="{href}" rel="me noopener" target="_blank">{label}</a>' for href, label in EXT
) + f"""
        </nav>
      </div>
      <div class="site-footer__bottom caption">
        <span>新竹 · 台灣</span>
        <span class="mono-sm">最後更新 {UPDATED}</span>
      </div>
    </div>
  </footer>

  <script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


def section(kicker, title, body, more=None, more_label=None):
    more_html = (f'\n        <a class="section__more body-sm" href="{more}">{more_label} →</a>'
                 if more else "")
    return f"""    <section class="section wrap wrap--wide reveal">
      <p class="section__kicker label">{kicker}</p>
      <div class="section__row">
        <h2 class="section__title h1">{title}</h2>{more_html}
      </div>
      <div class="section__body">
{body}
      </div>
    </section>
"""


def page_head_block(kicker, title, intro):
    return f"""    <div class="wrap wrap--wide page-head">
      <p class="page-head__kicker label">{kicker}</p>
      <h1 class="page-head__title display-l">{title}</h1>
      <p class="page-head__intro body">{intro}</p>
    </div>
"""


def card(title, href, status, desc, stats):
    stat_html = "".join(f"<span>{s}</span>" for s in stats)
    status_html = f'<span class="tag tag--accent">{status}</span>' if status else ""
    return f"""        <article class="card">
          <div class="card__top">
            <h3 class="card__title h2"><a href="{href}">{title}</a></h3>
            {status_html}
          </div>
          <p class="card__desc body-sm">{desc}</p>
          <p class="card__stats mono-sm">{stat_html}</p>
        </article>"""


def cards(items):
    return '        <div class="card-grid">\n' + "\n".join(card(*i) for i in items) + "\n        </div>"


def pub(year, title, href, authors, venue, links):
    link_html = "".join(f'<span>·</span><a href="{h}">{t}</a>' for t, h in links)
    return f"""          <li class="pub-list__item">
            <span class="pub-list__year mono-sm">{year}</span>
            <div>
              <a class="pub-list__title h3" href="{href}">{title}</a>
              <p class="pub-list__authors body-sm">{authors}</p>
              <p class="pub-list__venue caption"><em>{venue}</em>{link_html}</p>
            </div>
          </li>"""


def pubs(items):
    return '        <ol class="pub-list">\n' + "\n".join(pub(*i) for i in items) + "\n        </ol>"


def entry(when, title, where, desc):
    return f"""          <li class="entry-list__item">
            <span class="entry-list__when mono-sm">{when}</span>
            <div>
              <h3 class="entry-list__title h3">{title}</h3>
              <p class="entry-list__where caption">{where}</p>
              <p class="entry-list__desc body-sm">{desc}</p>
            </div>
          </li>"""


def entries(items):
    return '        <ul class="entry-list">\n' + "\n".join(entry(*i) for i in items) + "\n        </ul>"


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)


TODO = lambda s: f"      <!-- TODO: {s} -->\n"

# =========================================================================
# 首頁
# =========================================================================
home = head(
    "Ian — 認知神經科學與教育科技",
    "我研究大腦如何處理語言。可攜式腦波儀、N400、以及能真的放進教室的英語能力評估工具。",
    "/",
) + header(None) + TODO("把 Hero 的姓名換成你希望對外顯示的名字（中文全名或 Ian）") + f"""    <div class="wrap wrap--wide hero">
      <h1 class="hero__name display-xl">Ian</h1>
      <p class="hero__lead lead">我研究大腦如何處理語言。目前用可攜式腦波儀量測 N400，試著把它變成真的能放進教室的英語能力評估工具。</p>
      <p class="hero__meta caption">
        <span class="hero__dot" aria-hidden="true"></span>
        <span>碩士生 · <a href="https://www.nycu.edu.tw/" target="_blank" rel="noopener">陽明交通大學 腦科技跨領域工程學程</a> · 新竹</span>
      </p>
      <p class="hero__actions">
        <a class="btn btn--primary" href="/cv.pdf">下載 CV</a>
        <a class="btn btn--secondary" href="{MAIL_HREF}">寄信給我</a>
      </p>
    </div>

""" + section(
    "SELECTED WORK", "近期研究",
    cards([
        ("EEG 雜訊處理管線", "/research/", "進行中",
         "為低通道可攜式裝置設計的自動去偽跡流程，把眼動與肌電從單次試驗中剝離，讓 N400 在教室環境也量得到。",
         ["MATLAB / EEGLAB", "32 ch", "2025–"]),
        ("N400 英語能力評估", "/research/", "進行中",
         "用語義違例句作業誘發 N400，測試它與傳統紙筆英語測驗的相關性，目標是一個 15 分鐘的課堂版本。",
         ["ERP", "EFL", "2024–"]),
    ]),
    more="/research/", more_label="全部研究",
) + section(
    "PUBLICATIONS", "精選論文",
    TODO("以下三筆為佔位資料，請換成真實的題目、作者列、期刊與連結；沒有 DOI 就把該連結整個拿掉") + pubs([
        ("2026", "Portable EEG N400 as a proxy measure of lexical proficiency in EFL learners",
         "#", "<strong>Ian Chen</strong>, C.-H. Lin, &amp; J.-X. Zhuang",
         "Journal of Neurolinguistics", [("DOI", "#"), ("PDF", "#")]),
        ("2025", "運動員反應抑制作業中的 P300 振幅差異：一個跨項目的比較",
         "#", "<strong>Ian Chen</strong> &amp; Y.-T. Hsu",
         "中華心理學刊", [("PDF", "#")]),
    ]),
    more="/publications/", more_label="全部論文",
) + section(
    "BUILDS", "開發",
    cards([
        ("ERP Viewer", "/dev/", "維護中",
         "瀏覽器裡直接開 .set 檔看波形的小工具，不用開 MATLAB 就能快速確認一筆資料有沒有壞掉。",
         ["JavaScript", "WebGL", "2025–"]),
        ("營隊報名系統", "/dev/", None,
         "為腦科學營隊寫的報名與分組工具，取代了原本每年重做一次的 Google 表單流程。",
         ["Cloudflare", "D1", "2024"]),
    ]),
    more="/dev/", more_label="全部專案",
) + section(
    "ABOUT", "關於",
    TODO("這兩段請用你自己的話重寫，這是整個網站最需要「像你」的地方") + """        <div class="prose body">
          <p>我在清華大學念教育與學習科技，現在在陽明交通大學的腦科技跨領域工程學程讀碩士。兩個背景加起來的結果是：我對「學習發生的時候大腦在做什麼」這件事有興趣，但更在意這些知識能不能變成教室裡真的用得上的東西。</p>
          <p>大學時做過國科會大專生研究計畫，也在語言與腦科學的實驗室待過。教學方面，我設計過六梯國小腦科學營隊，總共帶過一百多個學生自己接電極、看見自己的腦波。做研究和做課程對我來說是同一件事的兩面。</p>
        </div>""",
) + FOOTER

write("public/index.html", home)

# =========================================================================
# Research
# =========================================================================
research = head(
    "研究 — Ian",
    "EEG／ERP 方法學、N400 與語言處理、可攜式腦波裝置的訊號品質。",
    "/research/",
) + header("research") + page_head_block(
    "RESEARCH", "研究",
    "我的研究問題是：腦波能不能取代一部分傳統的語言能力測驗？要回答它，得同時處理訊號品質與教育現場的可行性兩件事。",
) + section(
    "TOPICS", "研究主題",
    TODO("研究興趣請換成你自己的描述，標籤也一併調整") + """        <div class="prose body">
          <p>我關心語義處理的電生理指標——特別是 N400——在個別差異上的解釋力。傳統上 ERP 研究靠 grand average 得到漂亮的波形，但教育應用需要的恰恰是被平均掉的那部分：這一個學生的反應。</p>
          <p>另一條線是訊號本身。可攜式裝置的通道少、阻抗高、環境噪音大，若要在教室量測，去偽跡流程必須是自動且保守的。這部分的工作比較像工程，但它決定了前一條線做不做得成。</p>
        </div>
        <p class="tag-row" style="margin-top: var(--space-6)">
          <span class="tag">ERP</span><span class="tag">N400</span><span class="tag">EEG 訊號處理</span><span class="tag">EFL 評量</span><span class="tag">個別差異</span>
        </p>""",
) + section(
    "PROJECTS", "專案",
    TODO("四張卡片的內容、狀態與底部資訊請依實際情況調整；不足四個就刪掉多的") + cards([
        ("EEG 雜訊處理管線", "#", "進行中",
         "為低通道可攜式裝置設計的自動去偽跡流程，把眼動與肌電從單次試驗中剝離，讓 N400 在教室環境也量得到。",
         ["MATLAB / EEGLAB", "32 ch", "2025–"]),
        ("N400 英語能力評估", "#", "進行中",
         "用語義違例句作業誘發 N400，測試它與傳統紙筆英語測驗的相關性，目標是一個 15 分鐘的課堂版本。",
         ["ERP", "EFL", "2024–"]),
        ("運動員 ERP 比較研究", "#", "投稿中",
         "比較不同運動項目選手在反應抑制作業中的 P300 振幅，檢驗專項訓練是否反映在注意力資源分配上。",
         ["P300", "n = 60", "2025"]),
        ("單次試驗分類", "#", None,
         "用機器學習從單次試驗判斷受試者是否偵測到語義違例，測試 ERP 特徵在個人層級的可分性。",
         ["Python", "分類", "2024"]),
    ]),
) + section(
    "METHODS", "方法與工具",
    """        <div class="prose body">
          <p>資料前處理以 EEGLAB 與 ERPLAB 為主，分析與視覺化在 MATLAB 與 Python 之間來回。統計上偏好把個別差異當成訊號而非雜訊，所以混合效應模型用得比重複量數變異數分析多。</p>
          <p>所有分析腳本都盡量寫成可重跑的形式。已發表研究的資料與程式碼，只要倫理審查允許，都會放上來。</p>
        </div>""",
) + FOOTER
write("public/research/index.html", research)

# =========================================================================
# Publications
# =========================================================================
publications = head(
    "論文 — Ian",
    "期刊論文、研討會發表與撰寫中的稿件。",
    "/publications/",
) + header("publications") + page_head_block(
    "PUBLICATIONS", "論文",
    "依年份由新到舊排列。可取得的稿件都附上 PDF 連結；資料與程式碼在倫理審查允許的範圍內公開。",
) + TODO("以下全部是佔位資料。請逐筆換成真實內容；沒有的連結請整個刪掉，不要留 # 的假連結") + section(
    "JOURNAL", "期刊論文",
    pubs([
        ("2026", "Portable EEG N400 as a proxy measure of lexical proficiency in EFL learners",
         "#", "<strong>Ian Chen</strong>, C.-H. Lin, &amp; J.-X. Zhuang",
         "Journal of Neurolinguistics", [("DOI", "#"), ("PDF", "#"), ("Data", "#")]),
        ("2025", "運動員反應抑制作業中的 P300 振幅差異：一個跨項目的比較",
         "#", "<strong>Ian Chen</strong> &amp; Y.-T. Hsu",
         "中華心理學刊", [("PDF", "#")]),
    ]),
) + section(
    "CONFERENCE", "研討會發表",
    pubs([
        ("2025", "An automatic artifact rejection pipeline for low-density mobile EEG",
         "#", "<strong>Ian Chen</strong>",
         "Society for Neuroscience Annual Meeting, San Diego", [("Poster", "#")]),
        ("2024", "以腦波指標評估國小學童英語詞彙熟悉度的可行性",
         "#", "<strong>Ian Chen</strong>, J.-X. Zhuang",
         "台灣教育傳播暨科技學會年會，台北", [("Slides", "#")]),
    ]),
) + section(
    "IN PREPARATION", "撰寫中",
    pubs([
        ("2026", "Single-trial classification of semantic violation detection in L2 readers",
         "#", "<strong>Ian Chen</strong>, et al.",
         "準備投稿中", []),
    ]),
) + FOOTER
write("public/publications/index.html", publications)

# =========================================================================
# Teaching
# =========================================================================
teaching = head(
    "教學 — Ian",
    "國小腦科學營隊、課程設計與助教經驗。",
    "/teaching/",
) + header("teaching") + page_head_block(
    "TEACHING", "教學",
    "我設計課程的方式和做研究一樣：先問學生會在哪裡卡住，再決定要教什麼。動手做永遠排在講解前面。",
) + section(
    "PROGRAMS", "課程設計與營隊",
    TODO("梯次、時間、人數與課程名稱請換成真實資料") + entries([
        ("2022–2025", "國小腦科學營隊", "新竹市／共六梯，142 人次",
         "五天的動手做課程，四到六年級。學生自己接電極、看見自己的腦波，最後分組設計一個小實驗並報告。教案與學習單皆自製。"),
        ("2023", "「大腦與學習」教師工作坊", "國小教師研習，單場 6 小時",
         "把學習科學的研究結果翻譯成教室裡能用的具體做法，重點放在間隔複習與提取練習。"),
        ("2021–2022", "科學探究社團", "課後社團，每週兩小時",
         "以問題導向的方式帶學生跑完一個完整的探究循環，從提問到做出可展示的成果。"),
    ]),
) + section(
    "ASSISTANTSHIP", "助教經驗",
    TODO("課名、學期與系所請換成真實資料") + entries([
        ("2025 秋", "生醫訊號處理", "陽明交通大學 電機學院",
         "負責 MATLAB 實作課的設計與批改，把每週作業改成可自動驗證的形式，讓回饋在 24 小時內回到學生手上。"),
        ("2023 春", "學習科技導論", "清華大學 教育與學習科技學系",
         "帶討論課與期末專案指導。"),
    ]),
) + section(
    "APPROACH", "教學理念",
    """        <div class="prose body">
          <p>我相信先動手再講理論。腦科學營隊的第一堂課不是投影片，是讓學生把電極貼到自己頭上——當他們在螢幕上看見自己眨眼造成的那道尖波時，後面要講的所有東西都有了依附的對象。</p>
          <p>另一個原則是短回饋。一個單元的長度盡量控制在學生還記得起點的範圍內，讓每一次練習都能立刻看到結果。這對我自己也一樣有效。</p>
        </div>""",
) + FOOTER
write("public/teaching/index.html", teaching)

# =========================================================================
# Dev
# =========================================================================
dev = head(
    "開發 — Ian",
    "自己寫來解決自己問題的工具、網站與服務。",
    "/dev/",
) + header("dev") + page_head_block(
    "DEV", "開發",
    "多半是為了解決自己研究或教學上的麻煩而寫的東西。做得起來的就留著，做不起來的也記在這裡。",
) + section(
    "TOOLS", "工具",
    TODO("專案卡請換成你實際做過的東西；連結指向 repo 或線上版本") + cards([
        ("ERP Viewer", "#", "維護中",
         "瀏覽器裡直接開 .set 檔看波形的小工具，不用開 MATLAB 就能快速確認一筆資料有沒有壞掉。",
         ["JavaScript", "WebGL", "2025–"]),
        ("營隊報名系統", "#", None,
         "為腦科學營隊寫的報名與分組工具，取代了原本每年重做一次的 Google 表單流程。",
         ["Cloudflare", "D1", "2024"]),
        ("EEG 批次前處理 CLI", "#", "維護中",
         "把固定的前處理步驟包成一行指令，讓新進實驗室成員不必先學會整套 EEGLAB 的 GUI 操作。",
         ["Python", "MNE", "2025–"]),
        ("這個網站", "#", None,
         "純 HTML/CSS，部署在 Cloudflare Pages。所有樣式來自一套自己寫的 design system。",
         ["HTML / CSS", "Cloudflare", "2026"]),
    ]),
) + section(
    "NOTES", "寫在這裡的原因",
    """        <div class="prose body">
          <p>學術網站通常只放論文，但研究過程中真正花掉最多時間的往往是那些沒人會引用的工具。把它們寫出來，一方面是給未來的自己備忘，一方面是如果有人遇到同樣的問題，可以少走一段。</p>
        </div>""",
) + FOOTER
write("public/dev/index.html", dev)

# =========================================================================
# Notes（結構先備好，尚未開放；導覽列不顯示，且 noindex）
# =========================================================================
notes = head(
    "筆記 — Ian",
    "研究與教學過程中的筆記。",
    "/notes/",
    noindex=True,
) + header(None) + page_head_block(
    "NOTES", "筆記",
    "這一頁還沒開放。結構與樣式都已經備好，要開始寫的時候把下面註解掉的列表打開、並在 header 的導覽列加上一行即可。",
) + """    <section class="section wrap wrap--wide reveal">
      <div class="section__body">
        <div class="prose body">
          <p>目前沒有公開的文章。</p>
        </div>

        <!-- 開站步驟：
             1. 把 build 時的 NAV 陣列（或各頁 header 區塊）加入 ("/notes/", "NOTES", "notes")
             2. 移除本頁 head 裡的 noindex
             3. 把下面的列表取消註解，每篇文章建立 /notes/<slug>/index.html
             4. sitemap.xml 加上新頁面
        -->
        <!--
        <ul class="note-list">
          <li class="note-list__item"><a href="/notes/grand-average/">
            <span class="note-list__head">
              <span class="note-list__date mono-sm">2026.08</span>
              <span class="note-list__title h3">為什麼我不再相信 grand average</span>
            </span>
            <p class="note-list__excerpt body-sm">平均化讓 ERP 好看，但也把個別差異抹掉了。記一次重新分析舊資料的過程。</p>
          </a></li>
        </ul>
        -->
      </div>
    </section>
""" + FOOTER
write("public/notes/index.html", notes)
