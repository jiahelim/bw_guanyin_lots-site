"""Build the divine lots micro site from the transcribed lot data.

Reads  lots/data/raw/lot-{n}.json  (one file per lot, transcribed from assets/img/lot/lotC{n}.jpg + lotE{n}.jpg)
Writes lots/data/lots.json         (all lots merged, for anything else that wants the data)
       lots/index.html             (all 100 lots)
       lots/{n}.html               (one page per lot, EN and 中文 both in the page, switched by assets/js/lang.js)

Run from anywhere:  python DevineLot/tools/build_lots.py
"""
import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOTS = ROOT / "lots"
RAW = LOTS / "data" / "raw"
TOTAL = 100

DONATION_URL = "https://offering.bwmonastery.org.sg/"
MONASTERY_URL = "https://bwmonastery.org.sg/guanyinqian/lots"

ZH_KEYS = ["grade", "poem", "jieyue", "shiyi", "explain", "divination", "items", "summary"]
EN_KEYS = ["grade", "verse", "interpretation", "meaning", "explain", "divination", "items", "summary"]


def load():
    lots, problems = [], []
    for n in range(1, TOTAL + 1):
        path = RAW / f"lot-{n}.json"
        if not path.exists():
            problems.append(f"lot {n}: missing {path.name}")
            continue
        lot = json.loads(path.read_text(encoding="utf-8"))
        if lot.get("n") != n:
            problems.append(f"lot {n}: file says n={lot.get('n')}")
        for lang, keys in (("zh", ZH_KEYS), ("en", EN_KEYS)):
            missing = [k for k in keys if k not in lot.get(lang, {})]
            if missing:
                problems.append(f"lot {n}: {lang} missing {', '.join(missing)}")
        lots.append(lot)
    return lots, problems


def grade_class(zh_grade):
    if "上" in zh_grade:
        return "good"
    if "下" in zh_grade:
        return "bad"
    return "mid"


def both(en, zh):
    """Inline text in both languages; lang.js hides the inactive one."""
    return f'<span data-lang="en">{escape(en)}</span><span data-lang="zh">{escape(zh)}</span>'


def lines(items):
    if isinstance(items, str):
        items = [items]
    return "".join(f"<p>{escape(s)}</p>" for s in items if s)


def verse(items):
    """Half-lines in a two-column grid. Anything past the usual four (lot 87's 另： note) goes below as prose."""
    grid = '<div class="verse-lines">' + "".join(f"<span>{escape(s)}</span>" for s in items[:4]) + "</div>"
    return grid + lines(items[4:])


def page(title, body, depth_css="assets/lots.css", lang_js="../assets/js/lang.js", extra_head="", bootstrap=False):
    # Bootstrap loads before lots.css so the sheet styles keep the last word
    bootstrap_css = '<link rel="stylesheet" href="../assets/vendor/bootstrap/css/bootstrap.min.css">\n' if bootstrap else ""
    return f"""<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
{bootstrap_css}<link rel="stylesheet" href="{depth_css}">
<script src="{lang_js}"></script>
{extra_head}</head>
<body>
<header class="topbar">
  <div class="wrap">
    <a class="brand" href="index.html">{both("Guan Yin Divine Lots", "观音灵签")}</a>
    <nav>
      <a class="btn primary" href="../index1.html">{both("Draw a lot", "求签")}</a>
      <a class="btn" href="{DONATION_URL}" target="_blank" rel="noopener">{both("Offerings", "供养")}</a>
    </nav>
    <div id="langToggle"></div>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="wrap">
  <a href="{MONASTERY_URL}">{both("BW Monastery", "吉祥宝聚寺")}</a>
</footer>
</body>
</html>
"""


SERVICE = f"""<section class="card service" id="service">
  <h2>{both("Lot Interpretation Service", "解签服务")}</h2>
  <div class="body">
    <p data-lang="en">Unclear about the divination lot? Our on-site experienced interpreters are here to assist you, free of charge.</p>
    <p data-lang="zh">求了灵签看不明白？解签师在此为您免费解答疑惑！</p>
    <div class="venue">
      <strong>{both("BW Monastery, Guanyin Hall (Level 1)", "吉祥宝聚寺，观音殿（1楼）")}</strong>
      <address>1 Woodlands Drive 16 No.1 Singapore 737764</address>
      <p>{both("Mon–Fri", "星期一至五")} 11.30am – 1.30pm<br>
         {both("Weekends", "周末")} 10.30am – 12.30pm, 1.00pm – 3.00pm</p>
    </div>
    <div class="venue">
      <strong>{both("BW Monastery, Guanyin Hall (Bencoolen)", "吉祥宝聚寺位于明古莲大厦，观音殿")}</strong>
      <address>180 Bencoolen St #01-03 The Bencoolen Singapore 189646</address>
      <p>9.30am – 5pm</p>
    </div>
  </div>
</section>"""


AMA_EN_URL = "https://bwmonastery.org.sg/ama-buddhism-general"
AMA_ZH_URL = "https://bwmonastery.org.sg/chinese-ama-buddhism"
AMA_EN_FORM = "https://bwm.sg/amaform"
AMA_ZH_FORM = "https://bwmonastery.fillout.com/ama"


def ama_topic(title, example):
    return (
        f'<div class="col-md-4 mb-3"><div class="ama-topic h-100 p-3 bg-white border rounded">'
        f'<h3 class="h6 font-weight-bold mb-2">{escape(title)}</h3>'
        f'<p class="small text-muted mb-0">{escape(example)}</p></div></div>'
    )


# PLACEHOLDER: Ask-Me-Anything promo, wording taken from the AMA pages linked below. Session dates left out on purpose.
AMA = f"""<!-- PLACEHOLDER: Ask Me Anything (AMA) section -->
<section class="ama my-4 p-4 rounded" id="ama">
  <div data-lang="en">
    <p class="ama-eyebrow text-uppercase small font-weight-bold mb-1">Questions your lot didn't answer?</p>
    <h2 class="h4 font-weight-bold mb-2">Ask Me Anything (AMA) on Buddhism</h2>
    <p class="mb-3">A free 2-hour practical conversation about work, family and the thoughts you carry home. Not a religious commitment. Ask live, or submit questions anonymously from your phone.</p>
    <div class="row">
      {ama_topic("Managing Relationships", "Dealing with a difficult boss or colleague, and improving communication with a partner.")}
      {ama_topic("Sickness and Death", "Coping with grief, and talking about death with family.")}
      {ama_topic("General Buddhism", "Impermanence and uncertainty, and why Buddhism focuses on suffering.")}
    </div>
    <a class="btn btn-danger primary mr-2 mb-2" href="{AMA_EN_FORM}" target="_blank" rel="noopener">Reserve a seat</a>
    <a class="btn btn-outline-secondary mb-2" href="{AMA_EN_URL}" target="_blank" rel="noopener">Find out more</a>
  </div>
  <div data-lang="zh">
    <p class="ama-eyebrow small font-weight-bold mb-1">签文之外，还有疑问？</p>
    <h2 class="h4 font-weight-bold mb-2">AMA 佛法问答华语讲座</h2>
    <p class="mb-3">来参加我们的开放对话，分享佛法智慧，学习如何用新视角看待挑战。实用智慧，无关信仰。你可以现场发言提问，也可以通过匿名平台实时提交问题。</p>
    <div class="row">
      {ama_topic("事业瓶颈与职场焦虑", "加班文化依旧，体力却不如从前，健康开始亮红灯。")}
      {ama_topic("婚姻倦怠与孤独感", "夫妻变成“室友”，为柴米油盐争吵，却不再交心。")}
      {ama_topic("存在意义的迷茫", "奋斗半生，突然问自己：“这就是我想要的生活吗？”")}
    </div>
    <a class="btn btn-danger primary mr-2 mb-2" href="{AMA_ZH_FORM}" target="_blank" rel="noopener">报名</a>
    <a class="btn btn-outline-secondary mb-2" href="{AMA_ZH_URL}" target="_blank" rel="noopener">了解更多</a>
  </div>
</section>"""


def items_list(pairs):
    """事项 / Celestial Message: one 'label：verdict' per line, as on the printed sheet."""
    if not pairs:
        return ""
    # A few lots (84, 86, 90, 91, 100) print this section as prose, stored as one pair with an empty key
    if all(not k for k, _ in pairs):
        return lines([v for _, v in pairs])
    items = "".join(f'<li><span class="k">{escape(k)}</span><span class="v">{escape(v)}</span></li>' for k, v in pairs)
    return f'<ul class="items">{items}</ul>'


def rows(pairs):
    """Label-left table rows; rows with no content are skipped."""
    return "".join(f'<tr><th scope="row">{label}</th><td>{body}</td></tr>' for label, body in pairs if body)


# Red cloud motif for the interpretation box corners, defined once per page and reused four times
CLOUD_SYMBOL = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="cloud" viewBox="0 0 64 64">
    <g fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round">
      <path d="M3 61V27C3 13 13 3 27 3h34"/>
      <path d="M12 52V30c0-10 8-18 18-18h22"/>
      <path d="M22 40a8 8 0 1 1 8 8a4.5 4.5 0 1 1 4.5-4.5"/>
      <path d="M40 22a6 6 0 1 1 6 6"/>
      <path d="M18 22a5 5 0 1 1 5 5"/>
    </g>
    <circle cx="27" cy="27" r="2.6" fill="currentColor"/>
  </symbol>
</svg>"""

CORNERS = "".join(f'<svg class="corner {c}" aria-hidden="true"><use href="#cloud"/></svg>' for c in ("tl", "tr", "bl", "br"))


def sheet(lang, n, banner, lot_line, oracle_rows, interp_rows):
    """One printed lot sheet: banner, lot line, oracle box, interpretation box, page number."""
    return f"""<article class="sheet sheet-{lang}" data-lang="{lang}">
  {banner}
  <h1 class="lot-line">{lot_line}</h1>
  <div class="oracle-frame"><table class="oracle">{rows(oracle_rows)}</table></div>
  <div class="interp">{CORNERS}<table>{rows(interp_rows)}</table></div>
  <div class="page-no">{n}</div>
</article>"""


def lot_page(lot):
    n, zh, en = lot["n"], lot["zh"], lot["en"]

    zh_sheet = sheet(
        "zh", n,
        '<div class="banner-zh" role="img" aria-label="观音灵签">'
        '<span>观</span><i></i><span>音</span><i></i><span>灵</span><i></i><span>签</span></div>',
        f'第 <b>{n}</b> 签<span class="gap"></span>吉凶：<b>{escape(zh["grade"])}</b>',
        [
            ("签诗", f'<div class="verse">{verse(zh["poem"])}</div>'),
            ("解曰", f'<div class="jieyue">{verse(zh["jieyue"])}</div>'),
            ("诗意", f'<div class="shiyi">{lines(zh["shiyi"])}</div>'),
        ],
        [
            ("签诗", lines(zh["explain"])),
            ("签解", lines(zh["divination"])),
            ("事项", items_list(zh["items"])),
            ("签语", lines(zh.get("summary") or "")),
        ],
    )

    en_sheet = sheet(
        "en", n,
        '<div class="banner-en"><span>Goddess Of Mercy Divine Lots</span></div>',
        f'<span>Lot: <b>{n}</b></span><span class="gap"></span><span>Prophesy: <b>{escape(en["grade"])}</b></span>',
        [
            ("Lot Verse", f'<div class="verse">{lines(en["verse"])}</div>'),
            ("Interpret&shy;ation", lines(en["interpretation"])),
            ("Meaning Of This Lot", lines(en["meaning"])),
        ],
        [
            ("Lot Verse Interpret&shy;ation", lines(en["explain"])),
            ("Divination of The Lot", lines(en["divination"])),
            ("Celestial Message", items_list(en["items"])),
            ("Summary", lines(en.get("summary") or "")),
        ],
    )

    source = (
        f'<p class="source">'
        f'<a data-lang="en" href="../assets/img/lot/lotE{n}.jpg">View the original lot sheet</a>'
        f'<a data-lang="zh" href="../assets/img/lot/lotC{n}.jpg">查看原签图</a></p>'
    )

    body = "\n".join([CLOUD_SYMBOL, zh_sheet, en_sheet, AMA, SERVICE, source])
    return page(f"第{n}签 · Lot {n} · 观音灵签", body, bootstrap=True)


INDEX_SCRIPT = """<script>
document.addEventListener('DOMContentLoaded', function () {
  var buttons = document.querySelectorAll('.filters button');
  var cells = document.querySelectorAll('.grid li');
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener('click', function () {
      var grade = this.getAttribute('data-grade');
      for (var b = 0; b < buttons.length; b++) buttons[b].setAttribute('aria-pressed', buttons[b] === this);
      for (var c = 0; c < cells.length; c++) cells[c].hidden = grade !== 'all' && cells[c].getAttribute('data-grade') !== grade;
    });
  }
});
</script>
"""


def index_page(lots):
    cells = []
    for lot in lots:
        n, zh, en = lot["n"], lot["zh"], lot["en"]
        cls = grade_class(zh["grade"])
        first_zh = zh["poem"][0] if zh["poem"] else ""
        cells.append(
            f'<li data-grade="{cls}"><a href="{n}.html">'
            f'<span class="n">{both(f"Lot {n}", f"第{n}签")}</span>'
            f'<span class="g {cls}">{both(en["grade"], zh["grade"])}</span>'
            f'<span class="line" lang="zh">{escape(first_zh)}</span></a></li>'
        )
    body = f"""<div class="hero">
  <h1>{both("Divine Lots", "观音灵签")}</h1>
  <p>{both("All 100 lots of the Goddess of Mercy. Draw one, or read any lot below.", "观世音菩萨灵签一百首。可先求签，或直接阅读签文。")}</p>
  <a class="btn primary" href="../index1.html">{both("Draw a lot", "求签")}</a>
</div>
<div class="filters">
  <button class="btn" type="button" data-grade="all" aria-pressed="true">{both("All", "全部")}</button>
  <button class="btn" type="button" data-grade="good" aria-pressed="false">{both("Upper", "上签")}</button>
  <button class="btn" type="button" data-grade="mid" aria-pressed="false">{both("Middle", "中签")}</button>
  <button class="btn" type="button" data-grade="bad" aria-pressed="false">{both("Lower", "下签")}</button>
</div>
<ul class="grid">
{chr(10).join(cells)}
</ul>"""
    return page("观音灵签 · Guan Yin Divine Lots", body, extra_head=INDEX_SCRIPT)


def main():
    lots, problems = load()
    for p in problems:
        print("WARN", p, file=sys.stderr)
    (LOTS / "data" / "lots.json").write_text(json.dumps(lots, ensure_ascii=False, indent=1), encoding="utf-8")
    for lot in lots:
        (LOTS / f"{lot['n']}.html").write_text(lot_page(lot), encoding="utf-8")
    (LOTS / "index.html").write_text(index_page(lots), encoding="utf-8")
    print(f"built {len(lots)} lot pages + index into {LOTS}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
