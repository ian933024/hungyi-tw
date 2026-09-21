# -*- coding: utf-8 -*-
"""頁面產生器：把共用的 header/footer 與各頁的雙語內容組成純靜態 HTML。

產出的是純 HTML/CSS，網站本身不需要任何建置步驟；這支腳本只是為了讓
導覽列、頁尾、信箱這類重複區塊改一次就好。改完執行：

    python3 tools/build_pages.py

中英文兩種版本都寫進同一份 HTML，靠 CSS（:root[data-lang]）顯示其中一種。
"""
import os, io

SITE = "https://hungyi-tw.net"
UPDATED = "2026.09.21"
MAIL_DISPLAY = "ian933024 [at] gmail.com"
MAIL_HREF = "mailto:ian933024@gmail.com"
GITHUB = "https://github.com/ian933024"

# TODO: 以下兩位老師的英文拼法資料裡沒有，是用通行拼法填的，請確認後修改。
ADVISOR_KO_EN = "Li-Wei Ko"        # 柯立偉
ADVISOR_CHUANG_EN = "Chun-Hsiang Chuang"  # 莊鈞翔

NAV = [
    ("/research/",     "RESEARCH",     "research"),
    ("/publications/", "PUBLICATIONS", "publications"),
    ("/teaching/",     "TEACHING",     "teaching"),
    ("/dev/",          "DEV",          "dev"),
]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Newsreader:opsz,wght@6..72,400;6..72,500'
         '&amp;family=Noto+Serif+TC:wght@400;500'
         '&amp;family=IBM+Plex+Sans:wght@400;500;600'
         '&amp;family=IBM+Plex+Sans+TC:wght@400;500;600'
         '&amp;family=IBM+Plex+Mono:wght@400&amp;display=swap">')

BOOT = """<script>
    /* 在畫面繪製前套用語言與主題，避免切換時閃一下 */
    (function () {
      var r = document.documentElement;
      r.classList.remove('no-js');
      try {
        var l = localStorage.getItem('lang');
        if (l !== 'zh' && l !== 'en') l = /^zh/i.test(navigator.language || '') ? 'zh' : 'en';
        r.setAttribute('data-lang', l);
        r.setAttribute('lang', l === 'en' ? 'en' : 'zh-Hant-TW');
        var t = localStorage.getItem('theme');
        if (t === 'light' || t === 'dark') r.setAttribute('data-theme', t);
      } catch (e) {}
      setTimeout(function () { r.classList.add('reveal-fallback'); }, 2000);
    })();
  </script>"""


# --------------------------------------------------------------------------
# 雙語小工具
# --------------------------------------------------------------------------
def t(zh, en):
    """行內雙語片段。"""
    return '<span class="i18n-zh">' + zh + '</span><span class="i18n-en">' + en + '</span>'


def tb(tag, cls, zh, en):
    """區塊級雙語元素（整個元素換掉）。"""
    return ('<' + tag + ' class="' + cls + ' i18n-zh">' + zh + '</' + tag + '>'
            '<' + tag + ' class="' + cls + ' i18n-en">' + en + '</' + tag + '>')


def prose(pairs):
    """一組段落，每筆是 (中文, English)。"""
    zh = "".join('<p>' + a + '</p>' for a, b in pairs)
    en = "".join('<p>' + b + '</p>' for a, b in pairs)
    return ('        <div class="prose body i18n-zh">' + zh + '</div>\n'
            '        <div class="prose body i18n-en">' + en + '</div>')


# --------------------------------------------------------------------------
# 版面骨架
# --------------------------------------------------------------------------
def head(title_zh, title_en, desc_zh, desc_en, canonical, noindex=False):
    robots = '\n  <meta name="robots" content="noindex, nofollow">' if noindex else ''
    return ('<!DOCTYPE html>\n'
            '<html lang="zh-Hant-TW" data-lang="zh" class="no-js"\n'
            '      data-title-zh="' + title_zh + '" data-title-en="' + title_en + '"\n'
            '      data-desc-zh="' + desc_zh + '" data-desc-en="' + desc_en + '">\n'
            '<head>\n'
            '  <meta charset="utf-8">\n'
            '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '  <title>' + title_zh + '</title>\n'
            '  <meta name="description" content="' + desc_zh + '">' + robots + '\n'
            '  <link rel="canonical" href="' + SITE + canonical + '">\n'
            '  <meta property="og:type" content="website">\n'
            '  <meta property="og:title" content="' + title_zh + '">\n'
            '  <meta property="og:description" content="' + desc_zh + '">\n'
            '  <meta property="og:url" content="' + SITE + canonical + '">\n'
            '  <meta property="og:locale" content="zh_TW">\n'
            '  <meta property="og:locale:alternate" content="en_US">\n'
            '  <meta name="theme-color" content="#faf8f4" media="(prefers-color-scheme: light)">\n'
            '  <meta name="theme-color" content="#151412" media="(prefers-color-scheme: dark)">\n'
            '  <link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
            '  ' + FONTS + '\n'
            '  <link rel="stylesheet" href="/assets/css/tokens.css">\n'
            '  <link rel="stylesheet" href="/assets/css/site.css">\n'
            '  ' + BOOT + '\n'
            '</head>\n'
            '<body>\n'
            '  <a class="skip-link body-sm" href="#main">' + t('跳到主要內容', 'Skip to content') + '</a>\n')


def header(active):
    CUR = ' aria-current="page"'
    nav = "\n".join(
        '          <a href="%s"%s>%s</a>' % (href, CUR if key == active else "", label)
        for href, label, key in NAV
    )
    return ('  <header class="site-header">\n'
            '    <div class="wrap wrap--wide">\n'
            '      <div class="site-header__bar">\n'
            '        <a class="site-header__mark" href="/">' + t('余竑毅', 'Hung-Yi Yu') + '</a>\n'
            '        <nav class="site-nav label" aria-label="Main">\n'
            + nav + '\n'
            '        </nav>\n'
            '        <div class="site-header__aside label">\n'
            '          <a href="' + GITHUB + '" rel="me noopener" target="_blank">GITHUB</a>\n'
            '          <button class="lang-toggle" type="button" data-lang-toggle data-lang-label="en">EN</button>\n'
            '          <button class="theme-toggle" type="button" data-theme-toggle>DARK</button>\n'
            '        </div>\n'
            '      </div>\n'
            '    </div>\n'
            '  </header>\n\n'
            '  <main id="main">\n')


FOOTER = ('  </main>\n\n'
          '  <footer class="site-footer">\n'
          '    <div class="wrap wrap--wide site-footer__inner">\n'
          '      <div class="site-footer__cols">\n'
          '        <div>\n'
          '          <p class="site-footer__label label">CONTACT</p>\n'
          '          <a class="site-footer__mail" href="' + MAIL_HREF + '">' + MAIL_DISPLAY + '</a>\n'
          '        </div>\n'
          '        <nav class="site-footer__links label" aria-label="Links">\n'
          '          <a href="' + GITHUB + '" rel="me noopener" target="_blank">GITHUB</a>\n'
          '        </nav>\n'
          '      </div>\n'
          '      <div class="site-footer__bottom caption">\n'
          '        <span>' + t('新竹 · 台灣', 'Hsinchu, Taiwan') + '</span>\n'
          '        <span class="mono-sm">' + t('最後更新 ', 'Updated ') + UPDATED + '</span>\n'
          '      </div>\n'
          '    </div>\n'
          '  </footer>\n\n'
          '  <script src="/assets/js/site.js" defer></script>\n'
          '</body>\n'
          '</html>\n')


def section(kicker, title_zh, title_en, body, more=None, more_zh=None, more_en=None):
    more_html = ''
    if more:
        more_html = ('\n        <a class="section__more body-sm" href="' + more + '">'
                     + t(more_zh + ' →', more_en + ' →') + '</a>')
    return ('    <section class="section wrap wrap--wide reveal">\n'
            '      <p class="section__kicker label">' + kicker + '</p>\n'
            '      <div class="section__row">\n'
            '        ' + tb('h2', 'section__title h1', title_zh, title_en) + more_html + '\n'
            '      </div>\n'
            '      <div class="section__body">\n'
            + body + '\n'
            '      </div>\n'
            '    </section>\n')


def page_head_block(kicker, title_zh, title_en, intro_zh, intro_en):
    return ('    <div class="wrap wrap--wide page-head">\n'
            '      <p class="page-head__kicker label">' + kicker + '</p>\n'
            '      ' + tb('h1', 'page-head__title display-l', title_zh, title_en) + '\n'
            '      ' + tb('p', 'page-head__intro body', intro_zh, intro_en) + '\n'
            '    </div>\n')


def card(title_zh, title_en, href, status_zh, status_en, desc_zh, desc_en, stats):
    """stats: [(中文, English), ...]"""
    status = ''
    if status_zh:
        status = '<span class="tag tag--accent">' + t(status_zh, status_en) + '</span>'
    link_open = '<a href="' + href + '">' if href else '<span>'
    link_close = '</a>' if href else '</span>'
    stat_html = "".join('<span>' + t(a, b) + '</span>' for a, b in stats)
    return ('        <article class="card">\n'
            '          <div class="card__top">\n'
            '            <h3 class="card__title h2">' + link_open + t(title_zh, title_en) + link_close + '</h3>\n'
            '            ' + status + '\n'
            '          </div>\n'
            '          <p class="card__desc body-sm">' + t(desc_zh, desc_en) + '</p>\n'
            '          <p class="card__stats mono-sm">' + stat_html + '</p>\n'
            '        </article>')


def cards(items):
    return '        <div class="card-grid">\n' + "\n".join(card(*i) for i in items) + "\n        </div>"


def pub(year, title, authors_html, venue_zh, venue_en, note_zh, note_en):
    note = ''
    if note_zh:
        note = '<span>·</span><span>' + t(note_zh, note_en) + '</span>'
    return ('          <li class="pub-list__item">\n'
            '            <span class="pub-list__year mono-sm">' + year + '</span>\n'
            '            <div>\n'
            '              <p class="pub-list__title h3">' + title + '</p>\n'
            '              <p class="pub-list__authors body-sm">' + authors_html + '</p>\n'
            '              <p class="pub-list__venue caption"><em>' + t(venue_zh, venue_en) + '</em>' + note + '</p>\n'
            '            </div>\n'
            '          </li>')


def pubs(items):
    return '        <ol class="pub-list">\n' + "\n".join(pub(*i) for i in items) + "\n        </ol>"


def entry(when, title_zh, title_en, where_zh, where_en, desc_zh, desc_en):
    desc = ''
    if desc_zh:
        desc = '\n              <p class="entry-list__desc body-sm">' + t(desc_zh, desc_en) + '</p>'
    return ('          <li class="entry-list__item">\n'
            '            <span class="entry-list__when mono-sm">' + when + '</span>\n'
            '            <div>\n'
            '              <h3 class="entry-list__title h3">' + t(title_zh, title_en) + '</h3>\n'
            '              <p class="entry-list__where caption">' + t(where_zh, where_en) + '</p>' + desc + '\n'
            '            </div>\n'
            '          </li>')


def entries(items):
    return '        <ul class="entry-list">\n' + "\n".join(entry(*i) for i in items) + "\n        </ul>"


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)


# ==========================================================================
# 共用資料
# ==========================================================================
PROJECT_EEG = (
    "腦波雜訊特徵萃取方法之開發", "EEG Artifact Feature Extraction",
    "", "進行中", "Ongoing",
    "與工研院及鯨揚公司的產學合作計畫。蒐集各類腦波雜訊資料，並把它建成可參數化調整的雜訊模型，讓後續的去雜訊演算法有可控的測試素材。",
    "An industry project with ITRI and a partner company. We collect EEG artifact data and turn it into parameterised noise models, so that denoising algorithms have controllable material to be tested against.",
    [("陽明交大 神經工程實驗室", "NYCU Neural Engineering Lab"),
     ("指導 柯立偉", "Advisor " + ADVISOR_KO_EN),
     ("2026–", "2026–")],
)

PROJECT_PROMPT = (
    "使用編序教學法進行提示工程研究", "Programmed Instruction as Prompt Engineering",
    "", "已結案", "Completed",
    "國科會大專學生研究計畫。把編序教學法拆解步驟、逐步提示的邏輯套用到大型語言模型的提示設計，研究結果投稿至清華大學教育創新研討會。",
    "An NSTC Undergraduate Research Grant. I applied the step-wise logic of programmed instruction to prompt design for large language models; the results were submitted to the NTHU Conference on Educational Innovation.",
    [("國科會大專生計畫", "NSTC Grant"),
     ("指導 莊鈞翔", "Advisor " + ADVISOR_CHUANG_EN),
     ("2024–2025", "2024–2025")],
)

PUB_P300 = (
    "2026",
    "Task-Invariant P300 Responses in Athletes During Mathematical Tasks",
    "Chia-Chi Hsu, <strong>Hung-Yi Yu</strong>, Hui-Yu Hsu, Tsu-Jen Ding, Chen-Yu Yao, &amp; Zai-Fu Yao",
    "Psychonomic Society 2026 Annual Meeting", "Psychonomic Society 2026 Annual Meeting",
    "海報發表（已接受）", "Poster, accepted",
)

# ==========================================================================
# 首頁
# ==========================================================================
home = head(
    "余竑毅 — 腦科技與教育",
    "Hung-Yi Yu — Brain Technology and Education",
    "陽明交通大學腦科技碩士生。腦波訊號的雜訊處理，以及四年的教育現場經驗。",
    "Master&#39;s student in brain technology at NYCU. EEG noise characterisation, and four years of hands-on teaching.",
    "/",
) + header(None) + (
    '    <div class="wrap wrap--wide hero">\n'
    '      ' + tb('h1', 'hero__name display-xl', '余竑毅', 'Hung-Yi Yu') + '\n'
    '      ' + tb('p', 'hero__lead lead',
                 '我在陽明交通大學讀腦科技，研究腦波訊號裡的雜訊該怎麼描述與分離。在那之前我念教育，也在教學現場待了四年——對我來說這是同一個問題的兩端。',
                 'I study brain technology at NYCU, working on how to describe and separate noise in EEG signals. Before that I studied education and spent four years teaching. To me these are two ends of the same question.') + '\n'
    '      <p class="hero__meta caption">\n'
    '        <span class="hero__dot" aria-hidden="true"></span>\n'
    '        <span>' + t('碩士生 · 國立陽明交通大學 腦科技跨領域工程碩士學位學程 · 新竹',
                        'MSc student · Interdisciplinary Program of Brain Technology Engineering, NYCU · Hsinchu, Taiwan') + '</span>\n'
    '      </p>\n'
    '      <p class="hero__actions">\n'
    '        <a class="btn btn--primary" href="' + MAIL_HREF + '">' + t('寄信給我', 'Email me') + '</a>\n'
    '      </p>\n'
    '    </div>\n\n'
) + section(
    "ABOUT", "關於", "About",
    prose([
        ("我在清華大學念教育與學習科技，2026 年畢業後進入陽明交通大學電機學院的腦科技跨領域工程碩士學位學程，指導教授是柯立偉老師。目前在神經工程實驗室參與一個與工研院、鯨揚公司的產學合作計畫，負責蒐集腦波雜訊資料，並把它做成可參數化調整的雜訊訊號。",
         "I studied Education and Learning Sciences at National Tsing Hua University, and since 2026 I have been in the Interdisciplinary Program of Brain Technology Engineering at National Yang Ming Chiao Tung University, advised by Prof. " + ADVISOR_KO_EN + ". In the Neural Engineering Lab I work on an industry project with ITRI and a partner company, collecting EEG artifact data and turning it into parameterised noise signals."),
        ("在那之前，我在清大許慧玉老師的實驗室當研究助理，每週固定到台大醫院新竹分院進行腦波收案，對象是阿茲海默症與帕金森氏症的長者，同時也負責訓練其他收案人員。大學期間拿過國科會大專學生研究計畫，題目是把編序教學法的概念用在大型語言模型的提示工程上。",
         "Before that I was a research assistant in Prof. Hui-Yu Hsu&#39;s lab at NTHU, travelling weekly to NTUH Hsinchu Branch to collect EEG data from older adults with Alzheimer&#39;s and Parkinson&#39;s disease, and training other data collectors. As an undergraduate I held an NSTC Undergraduate Research Grant applying programmed-instruction principles to prompt engineering for large language models."),
        ("教學方面，我在清大教育服務團辦過與參與過二十場以上營隊，長期在尖石國中與東園國小做課輔，也帶過國中與國小的家教。另外有兩次赴日本的教育見習，2025 年那次擔任總召。",
         "On the teaching side, I ran or took part in more than twenty camps with the NTHU Education Service Corps, tutored long-term at Jianshi Junior High and Dongyuan Elementary School, and taught private students at both levels. I have also joined two education practicum trips to Japan, serving as coordinator for the 2025 one."),
    ]) + '\n'
    '        <p class="tag-row" style="margin-top: var(--space-6)">\n'
    '          <span class="tag">' + t('英語 CEFR B2', 'English CEFR B2') + '</span>'
    '<span class="tag">' + t('日語 JLPT N3', 'Japanese JLPT N3') + '</span>'
    '<span class="tag tag--highlight">' + t('國科會大專生計畫', 'NSTC Research Grant') + '</span>\n'
    '        </p>',
) + section(
    "RESEARCH", "研究計畫", "Research Projects",
    cards([PROJECT_EEG, PROJECT_PROMPT]),
    more="/research/", more_zh="研究全部", more_en="All research",
) + section(
    "PUBLICATIONS", "學術發表", "Presentations",
    pubs([PUB_P300]),
    more="/publications/", more_zh="全部發表", more_en="All presentations",
) + section(
    "TEACHING", "教學經驗", "Teaching",
    entries([
        ("2025–2026", "研究助理", "Research Assistant",
         "國立清華大學 許慧玉教授實驗室 · 台大醫院新竹分院",
         "Prof. Hui-Yu Hsu&#39;s Lab, NTHU · NTUH Hsinchu Branch",
         "負責腦波研究的收案與現場操作，熟悉無線乾式電極腦波帽，並對其他收案人員進行教學。",
         "Ran EEG data collection sessions, worked hands-on with wireless dry-electrode headsets, and trained other data collectors."),
        ("2023–2024", "教育服務團 幹部", "Education Service Corps, Officer",
         "國立清華大學", "National Tsing Hua University",
         "舉辦及參加超過二十場營隊。", "Organised and joined more than twenty camps."),
    ]),
    more="/teaching/", more_zh="全部教學經驗", more_en="All teaching",
) + FOOTER

write("public/index.html", home)

# ==========================================================================
# Research
# ==========================================================================
research = head(
    "研究 — 余竑毅", "Research — Hung-Yi Yu",
    "腦波雜訊特徵萃取、提示工程研究，以及臨床腦波收案經驗。",
    "EEG artifact feature extraction, prompt engineering research, and clinical EEG data collection.",
    "/research/",
) + header("research") + page_head_block(
    "RESEARCH", "研究", "Research",
    "我的研究圍繞腦波訊號本身：怎麼量得準、怎麼把雜訊和訊號分開，以及量到的東西能不能說明認知歷程的個別差異。",
    "My work centres on the EEG signal itself: how to measure it reliably, how to separate noise from signal, and whether what we measure can speak to individual differences in cognition.",
) + section(
    "PROJECTS", "研究計畫", "Projects",
    cards([PROJECT_EEG, PROJECT_PROMPT]),
) + section(
    "EXPERIENCE", "研究經歷", "Research Experience",
    entries([
        ("2025.06–2026.06", "研究助理", "Research Assistant",
         "國立清華大學 許慧玉教授實驗室 · 指導：許慧玉教授、姚在府教授",
         "Prof. Hui-Yu Hsu&#39;s Lab, NTHU · Advisors: Hui-Yu Hsu, Zai-Fu Yao",
         "每週固定前往台大醫院新竹分院進行腦波研究收案，對象為阿茲海默症或帕金森氏症之長者。熟悉無線乾式電極腦波帽的操作，並負責對其他收案人員進行教學。",
         "Travelled weekly to NTUH Hsinchu Branch to collect EEG data from older adults with Alzheimer&#39;s or Parkinson&#39;s disease. Experienced with wireless dry-electrode EEG headsets, and responsible for training other data collectors."),
    ]),
) + section(
    "TRAINING", "訓練與獎項", "Training and Awards",
    entries([
        ("2025.08", "MRI 安全講習", "MRI Safety Training",
         "國立成功大學", "National Cheng Kung University",
         "通過 MRI 安全講習考試並取得證書，具操作 MRI 實驗電腦資格。",
         "Passed the MRI safety certification exam; qualified to operate MRI experiment workstations."),
        ("2023.12", "教育大數據分析競賽", "Educational Big Data Analytics Competition",
         "教育部 · 全國賽入圍", "Ministry of Education · National finalist",
         "", ""),
    ]),
) + section(
    "METHODS", "方法與工具", "Methods and Tools",
    prose([
        ("訊號處理以 MATLAB 的 EEGLAB 與 ERPLAB 為主，分析與視覺化則在 MATLAB 與 Python 之間來回。相較於把個別差異當成需要平均掉的雜訊，我比較傾向把它當成訊號本身。",
         "Signal processing is mostly done in MATLAB with EEGLAB and ERPLAB; analysis and visualisation move between MATLAB and Python. Rather than treating individual differences as noise to be averaged away, I tend to treat them as the signal."),
        ("硬體上熟悉無線乾式電極腦波帽在非實驗室環境的操作——醫院診間、教室這類地方的訊號品質問題，是我研究雜訊的起點。",
         "On the hardware side, I am used to running wireless dry-electrode EEG headsets outside the lab. The signal-quality problems of clinics and classrooms are where my interest in artifacts began."),
    ]),
) + FOOTER

write("public/research/index.html", research)

# ==========================================================================
# Publications
# ==========================================================================
publications = head(
    "學術發表 — 余竑毅", "Presentations — Hung-Yi Yu",
    "研討會發表與學術產出。",
    "Conference presentations and academic output.",
    "/publications/",
) + header("publications") + page_head_block(
    "PUBLICATIONS", "學術發表", "Presentations",
    "依年份由新到舊排列。目前以研討會發表為主，期刊論文還在路上。",
    "Listed newest first. Conference work for now; journal articles are still on the way.",
) + section(
    "CONFERENCE", "研討會發表", "Conference Presentations",
    pubs([PUB_P300]),
) + FOOTER

write("public/publications/index.html", publications)

# ==========================================================================
# Teaching
# ==========================================================================
teaching = head(
    "教學 — 余竑毅", "Teaching — Hung-Yi Yu",
    "課輔、家教、營隊與海外教育見習經驗。",
    "Tutoring, camps, and education practicum experience in Taiwan and Japan.",
    "/teaching/",
) + header("teaching") + page_head_block(
    "TEACHING", "教學", "Teaching",
    "我的教學經驗大多不在標準的課堂裡：資源班、住宿生課輔、一對一家教。這些場景的共同點是進度表沒有用，得先知道學生卡在哪一步。",
    "Most of my teaching has happened outside standard classrooms: resource rooms, dormitory tutoring, one-on-one sessions. What they have in common is that a syllabus does not help; you first have to find the exact step where the student is stuck.",
) + section(
    "TUTORING", "教學與課輔", "Tutoring",
    entries([
        ("2023.09–2026.06", "家教 · 國中全科", "Private Tutor · Junior High, All Subjects",
         "一對一", "One-on-one",
         "為一位有特殊學習需求的國中生進行三年的全科教學，會考成績從 4C 提升至 2B2C（英文除外）。",
         "Three years of all-subject tutoring for a junior-high student with specific learning needs; entrance-exam results improved from 4C to 2B2C (excluding English)."),
        ("2025.03–2026.02", "家教 · 國小作文", "Private Tutor · Elementary Writing",
         "三位高年級學生", "Three upper-grade students",
         "為三位國小高年級學生設計並帶領作文課程，持續一年。",
         "Designed and taught a year-long writing course for three upper-grade elementary students."),
        ("2025.02–2025.06", "住宿生課輔教師", "Dormitory Tutor",
         "新竹縣尖石國中", "Jianshi Junior High School, Hsinchu County", "", ""),
        ("2022.09–2024.06", "資源班課輔教師", "Resource Room Tutor",
         "新竹市東園國小", "Dongyuan Elementary School, Hsinchu City", "", ""),
    ]),
) + section(
    "OUTREACH", "教育服務與海外見習", "Outreach and Practicum",
    entries([
        ("2023–2024", "教育服務團 幹部", "Education Service Corps, Officer",
         "國立清華大學 · 社團", "National Tsing Hua University · Student organisation",
         "舉辦及參加超過二十場營隊，負責課程設計與現場執行。",
         "Organised and joined more than twenty camps, responsible for curriculum design and on-site delivery."),
        ("2025.06", "日本大阪中華學校教育見習", "Education Practicum, Osaka Chinese School",
         "國立清華大學師資培育中心 · 總召",
         "NTHU Center for Teacher Education · Coordinator",
         "為期兩週的見習，規劃四堂以上入班文化交流課程，並在團隊中擔任總召，統籌公共事務。",
         "A two-week practicum. I designed more than four in-class cultural exchange lessons and served as team coordinator."),
        ("2024.06", "光罩日本教育見習計劃", "Japan Education Practicum Program",
         "國立清華大學／光照基金會 · 見習成員",
         "NTHU / Photomask Foundation · Participant",
         "前往日本愛媛，參訪當地幼兒園、國小、國中及高中，於幼兒園與國中進行試教，並以教師訪談進行跨國教育行動研究。",
         "Visited kindergartens through high schools in Ehime, Japan; taught trial lessons at a kindergarten and a junior high, and conducted cross-national action research through teacher interviews."),
    ]),
) + section(
    "APPROACH", "教學理念", "Approach",
    prose([
        ("先動手，再講理論。課輔和家教教會我的是：學生說「我不懂」的時候，通常不知道自己是在哪一步不懂——找到那一步比重講一次有用得多。",
         "Hands first, theory second. What tutoring taught me is that when a student says &ldquo;I don&#39;t get it&rdquo;, they usually cannot say which step lost them. Finding that step is far more useful than explaining the whole thing again."),
        ("這也是我後來對腦波感興趣的原因。如果能在學生說得出口之前，就看見理解有沒有發生，教學的回饋迴路會短很多。",
         "That is also why I became interested in EEG. If we could see whether comprehension is happening before a student can put it into words, the feedback loop of teaching would get a great deal shorter."),
    ]),
) + FOOTER

write("public/teaching/index.html", teaching)

# ==========================================================================
# Dev
# ==========================================================================
dev = head(
    "開發 — 余竑毅", "Builds — Hung-Yi Yu",
    "自己寫來解決研究與教學問題的工具與網站。",
    "Tools and sites built to solve my own research and teaching problems.",
    "/dev/",
) + header("dev") + page_head_block(
    "DEV", "開發", "Builds",
    "為了解決自己研究或教學上的麻煩而寫的東西。做得起來的就留著用。",
    "Things I built to solve problems in my own research and teaching. The ones that worked, I kept using.",
) + section(
    "PROJECTS", "專案", "Projects",
    cards([
        ("foliowl", "foliowl",
         "https://foliowl.hungyi-tw.net", "維護中", "Maintained",
         "版本化的個人經歷庫與學術履歷產生器。每一筆經歷存成可版本控制的條目，再依不同用途組合成履歷。這個網站的內容就是從它匯出的。",
         "A versioned personal experience archive and academic CV builder. Every entry is stored as a version-controlled record, then assembled into CVs for different purposes. The content of this site was exported from it.",
         [("Cloudflare Workers", "Cloudflare Workers"),
          ("foliowl.hungyi-tw.net", "foliowl.hungyi-tw.net"),
          ("2026–", "2026–")]),
        ("這個網站", "This site",
         "https://github.com/ian933024/hungyi-tw", "", "",
         "純 HTML 與 CSS，沒有框架也沒有建置步驟，部署在 Cloudflare Pages。所有顏色、字級與間距都來自一套自己寫的 design system。",
         "Plain HTML and CSS, no framework and no build step, deployed on Cloudflare Pages. Every colour, type size and spacing step comes from a design system I wrote for it.",
         [("HTML / CSS", "HTML / CSS"),
          ("Cloudflare Pages", "Cloudflare Pages"),
          ("2026", "2026")]),
    ]),
) + section(
    "WHY", "寫在這裡的原因", "Why These Are Here",
    prose([
        ("學術網站通常只放論文，但研究過程中真正花掉最多時間的，往往是那些沒有人會引用的工具。把它們寫出來，一方面是給未來的自己備忘，一方面是如果有人遇到同樣的問題，可以少走一段。",
         "Academic sites usually list only papers, but the things that eat the most time in research are often the tools nobody will ever cite. Writing them down is partly a note to my future self, and partly so that anyone hitting the same problem has a shorter path."),
    ]),
) + FOOTER

write("public/dev/index.html", dev)

# ==========================================================================
# Notes（結構先備好，尚未開放）
# ==========================================================================
notes = head(
    "筆記 — 余竑毅", "Notes — Hung-Yi Yu",
    "研究與教學過程中的筆記。", "Notes from research and teaching.",
    "/notes/", noindex=True,
) + header(None) + page_head_block(
    "NOTES", "筆記", "Notes",
    "這一頁還沒開放。結構與樣式都已經備好，要開始寫的時候把下面註解掉的列表打開、並在導覽列加上一行即可。",
    "This page is not open yet. The structure and styles are ready; uncomment the list below and add a nav entry when you want to start writing.",
) + ('    <section class="section wrap wrap--wide reveal">\n'
    '      <div class="section__body">\n'
    + prose([("目前沒有公開的文章。", "No public posts yet.")]) + '\n'
    '''
        <!-- 開站步驟：
             1. tools/build_pages.py 的 NAV 陣列加入 ("/notes/", "NOTES", "notes")
             2. 移除本頁 head() 呼叫裡的 noindex=True
             3. 把下面的列表取消註解，每篇文章建立 /notes/<slug>/index.html
             4. public/sitemap.xml 與 robots.txt 一併更新
        -->
        <!--
        <ul class="note-list">
          <li class="note-list__item"><a href="/notes/first-post/">
            <span class="note-list__head">
              <span class="note-list__date mono-sm">2026.10</span>
              <span class="note-list__title h3">文章標題</span>
            </span>
            <p class="note-list__excerpt body-sm">一句話摘要。</p>
          </a></li>
        </ul>
        -->
'''
    '      </div>\n'
    '    </section>\n') + FOOTER

write("public/notes/index.html", notes)
print("done")
