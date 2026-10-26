"""Build a small, self-contained GitHub profile using Python's standard library."""

import argparse
import base64
import datetime as dt
import json
import math
import os
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONO = "'Cascadia Code','JetBrains Mono',Consolas,monospace"
SANS = "'Segoe UI','Microsoft YaHei','Noto Sans CJK SC',sans-serif"
PINK = "#ff91ad"
BLUE = "#78c9ef"
STACK = [
    ("Go", "BACKEND", "#73d5e8"),
    ("Java", "BACKEND", "#f5b77d"),
    ("HTML", "WEB", "#ef9c85"),
    ("CSS", "WEB", "#94b9ff"),
    ("JavaScript", "WEB", "#f2d886"),
    ("Vue", "WEB", "#8ed8b0"),
    ("Python", "TOOLS", "#a6c4f5"),
    ("Rust", "SYSTEMS", "#e5b49d"),
]


def request(url, *, text=False):
    headers = {"User-Agent": "jibanso-profile", "Accept-Language": "en-US"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=25) as response:
                data = response.read().decode("utf-8")
            return data if text else json.loads(data)
        except (OSError, ValueError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def svg(width, height, body, label, *, defs="", background="#111d30"):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">
<title>{escape(label)}</title>
<defs>{defs}<clipPath id="frame"><rect width="{width}" height="{height}" rx="18"/></clipPath></defs>
<style>
text{{font-family:{SANS}}}.mono{{font-family:{MONO}}}
.moving{{display:inline}}.still{{display:none}}
</style>
<g clip-path="url(#frame)"><rect width="{width}" height="{height}" fill="{background}"/>{body}</g>
</svg>\n'''


def static_svg(source):
    """Build an actual still image; the README selects it for reduced motion."""
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    root = ET.fromstring(source)
    for parent in list(root.iter()):
        for child in list(parent):
            if "moving" in child.get("class", "").split() or child.tag.rsplit("}", 1)[-1] in {"animate", "animateTransform", "animateMotion", "set"}:
                parent.remove(child)
    for element in root.iter():
        if element.get("class") == "still":
            element.attrib.pop("class")
    return ET.tostring(root, encoding="unicode") + "\n"


def hero(username):
    portrait = base64.b64encode((ROOT / "assets/anon-stage.png").read_bytes()).decode("ascii")
    strings = "".join(f'<path d="M{460+i*22} 0L{95+i*22} 530" stroke="#7fc6ed" opacity=".1" stroke-dasharray="8 11"><animate attributeName="stroke-dashoffset" values="0;-114" dur="12s" begin="-{i*.8}s" repeatCount="indefinite"/></path>' for i in range(6))
    sparks = "".join(f'<circle cx="{85+i*73}" cy="{47+(i*47)%380}" r="{1+i%2}" fill="{PINK if i%2 else BLUE}" opacity=".35"><animate attributeName="opacity" values=".18;.8;.18" dur="{3+i%4}s" begin="-{i*.65}s" repeatCount="indefinite"/></circle>' for i in range(13))
    sparkles = ''.join(f'<g transform="translate({x} {y})"><path d="M0 -6L1.5 -1.5L6 0L1.5 1.5L0 6L-1.5 1.5L-6 0L-1.5 -1.5Z" fill="{color}" opacity=".45"><animate attributeName="opacity" values=".2;.85;.2" dur="4s" begin="-{index*.9}s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="scale" values=".75;1.15;.75" dur="4s" begin="-{index*.9}s" repeatCount="indefinite"/></path></g>' for index,(x,y,color) in enumerate([(574,96,PINK),(650,308,BLUE),(530,436,PINK),(903,419,BLUE)]))
    notes = ''.join(f'<g transform="translate({x} {y})"><text fill="{color}" font-size="{size}" opacity=".3">{note}<animate attributeName="opacity" values=".28;.65;.28" dur="5s" begin="-{index*1.3}s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 0;0 -9;0 0" dur="5s" begin="-{index*1.3}s" repeatCount="indefinite"/></text></g>' for index,(x,y,size,color,note) in enumerate([(562,163,30,BLUE,'♪'),(565,395,25,PINK,'♫'),(913,298,24,PINK,'♪')]))
    leds = ''.join(f'<circle cx="{215+index*10}" cy="46" r="1.8" fill="{PINK}" opacity=".4"><animate attributeName="opacity" values=".25;1;.25" dur="4s" begin="-{index*.3}s" repeatCount="indefinite"/></circle>' for index in range(5))
    chips = []
    for index, (name, _, color) in enumerate(STACK):
        x, y = 58 + (index % 4) * 120, 333 + (index // 4) * 49
        chips.append(f'<rect x="{x}" y="{y}" width="110" height="35" rx="6" fill="#fff" fill-opacity=".045" stroke="#a6c7e1" stroke-opacity=".2"/><circle cx="{x+12}" cy="{y+18}" r="3" fill="{color}"/><circle class="moving" cx="{x+12}" cy="{y+18}" r="3" fill="none" stroke="{color}"><animate attributeName="r" values="2.5;6;2.5" dur="3s" begin="-{index*.4}s" repeatCount="indefinite"/><animate attributeName="opacity" values=".6;0;.6" dur="3s" begin="-{index*.4}s" repeatCount="indefinite"/></circle><text x="{x+24}" y="{y+23}" fill="#eef4fc" font-size="14">{name}</text>')
    body = f'''
<rect width="1000" height="530" fill="url(#night)"/>
<path d="M690 0H1000V530H470Z" fill="#638bd0" opacity=".08"/>
<path d="M823 0H1000V530H610Z" fill="#ff9fb5" opacity=".12"/>
<g class="moving"><path d="M745 -80L270 530H1000Z" fill="url(#stage-beam)" opacity=".12"><animateTransform attributeName="transform" type="rotate" values="-7 760 -80;8 760 -80;-7 760 -80" dur="13s" repeatCount="indefinite"/><animate attributeName="opacity" values=".08;.2;.08" dur="13s" repeatCount="indefinite"/></path>{strings}{sparks}</g>
<circle cx="820" cy="200" r="230" fill="url(#pink-glow)"/>
<g class="moving">{sparkles}{notes}{leds}</g>
<text x="58" y="52" fill="{PINK}" font-size="19" font-weight="700" letter-spacing="2">MyGO!!!!!</text>
<text x="58" y="79" fill="#9bb5d3" font-size="11" class="mono" letter-spacing="2.5">AI CODING / A PERSONAL SETLIST</text>
<path d="M58 105H105" stroke="{PINK}" stroke-width="3"/>
<text x="52" y="206" fill="#f7f2f5" font-size="94" font-weight="800" letter-spacing="-4">{escape(username)}</text>
<text x="60" y="247" fill="{BLUE}" font-size="23" font-weight="600">Build with AI. Keep my own rhythm.</text>
<text x="60" y="282" fill="#bccbe0" font-size="17">AI 编程开发者 / 把想法做成作品。</text>
{''.join(chips)}
<image x="505" y="-188" width="632" height="1042" xlink:href="data:image/png;base64,{portrait}"/>
<path class="moving" d="M260 -30H350L40 530H-50Z" fill="url(#shine)" opacity="0"><animateTransform attributeName="transform" type="translate" values="-1200 0;-1200 0;1100 0;1100 0" keyTimes="0;.55;.85;1" dur="14s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;0;.25;0" keyTimes="0;.55;.7;1" dur="14s" repeatCount="indefinite"/></path>
<rect x="0" y="465" width="1000" height="65" fill="#091525" opacity=".88"/>
<path d="M58 488H122" stroke="{PINK}" stroke-width="3"/>
<text x="136" y="493" fill="#edf2fc" font-size="12" class="mono" letter-spacing="2">GO · JAVA · WEB · PYTHON · RUST</text>
<text x="940" y="493" fill="{PINK}" font-size="12" class="mono" text-anchor="end">ANON / GT.</text>
<text x="58" y="514" fill="#7e99b8" font-size="10" class="mono">JIBANSO — AI CODING DEVELOPER</text>
<g transform="translate(944 38)"><path d="M0 0V390" stroke="#d1d9ef" stroke-opacity=".24" stroke-dasharray="2 6"/><text transform="translate(22 5) rotate(90)" fill="#bbd4ed" font-size="10" class="mono" letter-spacing="3">CHIHAYA ANON / MyGO!!!!!</text></g>
'''
    defs = '<linearGradient id="night" x2="1" y2="1"><stop stop-color="#0d1c30"/><stop offset=".65" stop-color="#1a2844"/><stop offset="1" stop-color="#3e2d4b"/></linearGradient><radialGradient id="pink-glow"><stop stop-color="#ffb7cb" stop-opacity=".28"/><stop offset="1" stop-color="#ffb7cb" stop-opacity="0"/></radialGradient><linearGradient id="stage-beam" x2="0" y2="1"><stop stop-color="#ffacc4"/><stop offset="1" stop-color="#87c9f0" stop-opacity="0"/></linearGradient><linearGradient id="shine"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    return svg(1000, 530, body, f"{username} — AI 编程开发者 / 千早爱音与 MyGO!!!!! 主题主页", defs=defs)


def setlist():
    rows = []
    for index, (name, category, color) in enumerate(STACK):
        col, row = divmod(index, 4)
        x, y = 46 + col * 468, 116 + row * 43
        rows.append(f'<text x="{x}" y="{y}" fill="#bd5775" font-size="13" class="mono">{index+1:02d}</text><text x="{x+42}" y="{y}" fill="#263549" font-size="21" font-weight="650">{name}</text><text x="{x+393}" y="{y}" text-anchor="end" fill="#718196" font-size="10" class="mono" letter-spacing="1">{category}</text><path d="M{x} {y+14}H{x+394}" stroke="#d5dbe4"/><path class="moving" d="M{x} {y+14}H{x+394}" stroke="{color}" stroke-width="2" opacity=".65" stroke-dasharray="28 410"><animate attributeName="stroke-dashoffset" values="28;-410" dur="7s" begin="-{index*.7}s" repeatCount="indefinite"/></path>')
    body = f'''<path d="M0 0H1000V7H0Z" fill="{PINK}"/><rect class="moving" x="-320" y="0" width="320" height="7" fill="url(#ticket-glow)"><animate attributeName="x" values="-320;-320;1100;1100" keyTimes="0;.25;.7;1" dur="9s" repeatCount="indefinite"/></rect>
<text x="46" y="47" fill="#20354c" font-size="23" font-weight="750" letter-spacing="2">AI CODING SETLIST</text>
<text x="46" y="72" fill="#728294" font-size="11" class="mono">AI-ASSISTED / 8 LANGUAGES &amp; TECHNOLOGIES</text>
<g class="moving" transform="translate(872 56)"><text fill="#bd5775" font-size="24" opacity=".35">♫<animateTransform attributeName="transform" type="translate" values="0 0;0 -7;0 0" dur="5s" repeatCount="indefinite"/></text></g><g class="moving" transform="translate(913 48)"><text fill="#84afc8" font-size="17" opacity=".3">♪<animateTransform attributeName="transform" type="translate" values="0 0;0 -7;0 0" dur="5s" begin="-2s" repeatCount="indefinite"/></text></g>
{''.join(rows)}<path d="M960 30V294" stroke="#c5ccd6" stroke-dasharray="3 5"/><path class="moving" d="M960 30V294" stroke="#bd5775" opacity=".3" stroke-dasharray="3 45"><animate attributeName="stroke-dashoffset" values="0;-96" dur="14s" repeatCount="indefinite"/></path>
<text transform="translate(982 45) rotate(90)" fill="#9a667c" font-size="10" class="mono" letter-spacing="3">JIBANSO / ALL ACCESS</text>
<circle cx="0" cy="164" r="13" fill="#0d1117"/><circle cx="1000" cy="164" r="13" fill="#0d1117"/>'''
    defs = '<linearGradient id="ticket-glow"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    return svg(1000, 312, body, "开发语言与技术：Go、Java、HTML、CSS、JavaScript、Vue、Python、Rust", defs=defs, background="#f6f3f0")


def terminal(username, user, repos, now):
    stars = sum(repo["stargazers_count"] for repo in repos if not repo["fork"])
    stats = [("PUBLIC REPOS", user["public_repos"]), ("FOLLOWERS", user["followers"]), ("OWN REPO STARS", stars), ("TECHNOLOGIES", len(STACK))]
    blocks = []
    for index, (label, value) in enumerate(stats):
        x = 44 + index * 236
        blocks.append(f'<text x="{x}" y="324" fill="#8599b4" font-size="10" class="mono" letter-spacing="1.5">{label}</text><text x="{x}" y="365" fill="{PINK if index%2==0 else BLUE}" font-size="38" font-weight="650" class="mono">{value}</text>')
        if index < 3:
            blocks.append(f'<path d="M{x+204} 310V370" stroke="#304258"/>')
    equalizer, still_equalizer = [], []
    for i in range(18):
        height, duration = 12+(i%5)*4, 1.1+i%4*.25
        heights = ';'.join(f'{height*scale:.2f}' for scale in [.35,.9,.5,1,.35])
        positions = ';'.join(f'{84-height*scale:.2f}' for scale in [.35,.9,.5,1,.35])
        bar = f'<rect x="{748+i*10}" y="{84-height}" width="4" height="{height}" rx="2" fill="{PINK if i%4 else BLUE}" opacity=".65"'
        still_equalizer.append(bar+'/>')
        equalizer.append(bar+f'><animate attributeName="height" values="{heights}" dur="{duration}s" begin="-{i*.19}s" repeatCount="indefinite"/><animate attributeName="y" values="{positions}" dur="{duration}s" begin="-{i*.19}s" repeatCount="indefinite"/></rect>')
    body = f'''<rect width="1000" height="95" fill="#182b43"/>
<text x="44" y="38" fill="{PINK}" class="mono" font-size="11" letter-spacing="3">BACKSTAGE / AI CODING SESSION</text>
<text x="44" y="72" fill="#edf3fb" font-size="24" font-weight="650">{escape(username)}@github</text><g class="moving">{''.join(equalizer)}</g><g class="still">{''.join(still_equalizer)}</g>
<path class="moving" d="M44 94H956" stroke="{PINK}" opacity=".45" stroke-dasharray="28 410"><animate attributeName="stroke-dashoffset" values="28;-410" dur="7s" repeatCount="indefinite"/></path>
<rect class="moving" x="44" y="104" width="912" height="1" fill="{BLUE}" opacity="0"><animate attributeName="y" values="104;449" dur="12s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;.12;.12;0" keyTimes="0;.1;.9;1" dur="12s" repeatCount="indefinite"/></rect>
<text x="44" y="135" fill="{BLUE}" font-size="15" class="mono">&gt; whoami</text>
<text x="67" y="164" fill="#e0e8f4" font-size="15" class="mono">{escape(username)} / AI-assisted developer</text>
<text x="44" y="207" fill="{BLUE}" font-size="15" class="mono">&gt; cat workflow.txt</text>
<text x="67" y="237" fill="#d0ddec" font-size="15" class="mono">Ideas + AI coding + iteration / MyGO!!!!!</text>
<text x="44" y="280" fill="{BLUE}" font-size="15" class="mono">&gt; github --public-snapshot</text>
{''.join(blocks)}
<path d="M44 392H956" stroke="#304258"/>
<text x="44" y="420" fill="#889db8" font-size="11" class="mono">PUBLIC GITHUB DATA · {now:%Y-%m-%d %H:%M} UTC</text>
<text x="956" y="420" text-anchor="end" fill="#b7c9df" font-size="11" class="mono">KEEP BUILDING <tspan fill="{PINK}">!!!!!</tspan></text>
<rect class="moving" x="44" y="441" width="8" height="13" fill="{PINK}"><animate attributeName="opacity" values="1;0;1" keyTimes="0;.5;1" calcMode="discrete" dur="1.1s" repeatCount="indefinite"/></rect><rect class="still" x="44" y="441" width="8" height="13" fill="{PINK}"/>
<g class="moving" transform="translate(942 448)"><path d="M0 -5L1 -1L5 0L1 1L0 5L-1 1L-5 0L-1 -1Z" fill="{BLUE}" opacity=".4"><animate attributeName="opacity" values=".2;.8;.2" dur="4s" repeatCount="indefinite"/></path></g>
'''
    return svg(1000, 476, body, f"{username} 的公开 GitHub 统计", background="#111f32")


def contribution_days(username):
    html = request(f"https://github.com/users/{username}/contributions", text=True)
    days = {}
    for tag in re.findall(r"<td\b[^>]*>", html):
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', tag))
        date, level = attrs.get("data-date"), attrs.get("data-level")
        if date and level and re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            days[dt.date.fromisoformat(date)] = min(4, max(0, int(level)))
    if len(days) < 300:
        raise ValueError("GitHub contribution calendar is incomplete; keep the previous generated assets")
    return days


def snake(days, *, dark):
    bg, ink = ("#111f32", "#b9cee5") if dark else ("#f6f3f0", "#34485f")
    colors = ["#25354b", "#76465f", "#b65b7c", "#e17fa0", "#ffafc7"] if dark else ["#e4dfe2", "#efc1d0", "#e89ab4", "#d96994", "#ba4276"]
    start = min(days)
    weeks = ((max(days) - start).days // 7) + 1
    size, step = 11, 16
    left = (1000 - ((weeks-1)*step+size))/2
    cells = []
    for date, level in days.items():
        column = (date-start).days // 7
        row = (date.weekday()+1) % 7
        cells.append((column, row, date, level))
    cells.sort(key=lambda cell: (cell[0], cell[1] if cell[0] % 2 == 0 else -cell[1]))
    points = [(left+col*step+size/2, 83+row*step+size/2) for col,row,_,_ in cells]
    distance, distances = 0, [0]
    for previous, current in zip(points, points[1:]):
        distance += math.dist(previous, current)
        distances.append(distance)
    path = "M" + "L".join(f"{x:.1f},{y:.1f}" for x,y in points)
    rects, still_rects = [], []
    for (col,row,date,level), passed in zip(cells, distances):
        at = .025 + (passed / distance) * .91
        rect = f'<rect x="{left+col*step:.1f}" y="{83+row*step}" width="{size}" height="{size}" rx="2" fill="{colors[level]}"><title>{date}: contribution level {level}</title>'
        still_rects.append(rect+'</rect>')
        rects.append(rect+f'<animate attributeName="opacity" values="1;1;.18;.18;1" keyTimes="0;{at:.5f};{at+.003:.5f};.98;1" dur="36s" repeatCount="indefinite"/></rect>')
    legend = ''.join(f'<rect x="{832+i*17}" y="212" width="11" height="11" rx="2" fill="{color}"/>' for i,color in enumerate(colors))
    body = f'''<text x="44" y="37" fill="{PINK if dark else '#bd5775'}" font-size="11" class="mono" letter-spacing="2.8">ENCORE / CONTRIBUTIONS</text>
<text x="44" y="61" fill="{ink}" font-size="12">沿着每一次提交，继续往前。</text>
<g class="moving">{''.join(rects)}
<path d="{path}" fill="none" stroke="{PINK if dark else '#b94775'}" stroke-opacity=".13" stroke-width="18" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="55 100000"><animate attributeName="stroke-dashoffset" from="55" to="{-distance:.1f}" dur="36s" repeatCount="indefinite"/></path>
<path d="{path}" fill="none" stroke="{PINK if dark else '#b94775'}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="55 100000"><animate attributeName="stroke-dashoffset" from="55" to="{-distance:.1f}" dur="36s" repeatCount="indefinite"/></path>
</g><g class="still">{''.join(still_rects)}</g>
<text x="44" y="222" fill="{ink}" font-size="10" class="mono">{start:%Y.%m} — {max(days):%Y.%m} / PUBLIC CONTRIBUTION GRAPH</text>
<text x="795" y="221" fill="{ink}" font-size="10" class="mono">LESS</text>{legend}<text x="926" y="221" fill="{ink}" font-size="10" class="mono">MORE</text>'''
    return svg(1000, 248, body, "真实公开 GitHub 贡献图与粉色贪吃蛇动画", background=bg)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="jibanso")
    parser.add_argument("--out", type=Path, default=ROOT / "assets")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", args.username):
        parser.error("Invalid GitHub username")
    user = request(f"https://api.github.com/users/{args.username}")
    repos, page = [], 1
    while True:
        batch = request(f"https://api.github.com/users/{args.username}/repos?type=owner&per_page=100&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    days = contribution_days(args.username)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    images = {
        "hero.svg": hero(args.username),
        "setlist.svg": setlist(),
        "terminal.svg": terminal(args.username, user, repos, now),
        "contributions.svg": snake(days, dark=False),
        "contributions-dark.svg": snake(days, dark=True),
    }
    for name, content in list(images.items()):
        images[name.replace(".svg", "-still.svg")] = static_svg(content)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, content in images.items():
        (args.out / name).write_text(content, encoding="utf-8")
    print(f"Generated {len(images)} SVGs from public data, {len(days)} contribution days.")


if __name__ == "__main__":
    main()
