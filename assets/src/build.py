"""Builds the profile's self-hosted SVGs: assets/header-{light,dark}.svg and assets/stack-{light,dark}.svg.

    pip install fonttools brotli
    python assets/src/build.py

Space Grotesk is embedded as a subset, so the SVGs render the same everywhere and need no network.
Edit PHRASES, PIPELINE or STACK below, then rerun.
"""
import base64, io, pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset

SRC = pathlib.Path(__file__).resolve().parent
OUT = SRC.parent

NAME = "Josiah Steve Sam"
ROLE = "Full Stack AI Engineer"
PLACE = "Chennai, India"
BAR = "~/josiah"
PHRASES = [
    "building AI agents for web, chat and WhatsApp",
    "hybrid retrieval and reranking for grounded answers",
    "reading invoices and ID cards with document AI",
    "FastAPI backends and Next.js frontends",
]
PIPELINE = ["query", "hybrid search", "rerank", "grounded answer"]
STACK = [
    ("AI", [("LangGraph", "langgraph.svg"), ("LangChain", "langchain.png"), ("RAG", None),
            ("Hybrid retrieval & reranking", None), ("LiteLLM", "litellm.svg"), ("Guardrails", None),
            ("Langfuse", "langfuse.svg"), ("OpenAI API", "openai.png"), ("Hugging Face", "huggingface.svg"),
            ("PyTorch", "pytorch-original.svg"), ("OCR & document AI", None)]),
    ("Backend", [("Python", "python-original.svg"), ("FastAPI", "FastAPI.svg"),
                 ("Node.js", "nodejs-original.svg"), ("Express", "express-original.svg")]),
    ("Frontend", [("React", "react-original.svg"), ("Next.js", "nextjs-original.svg"),
                  ("JavaScript", "javascript-original.svg"), ("TypeScript", "Typescript.svg"),
                  ("Vite", "vitejs-original.svg")]),
    ("Data", [("PostgreSQL", "postgresql-original.svg"), ("Qdrant", "qdrant.svg"), ("Redis", "redis-original.svg"),
              ("MongoDB", "mongodb-original.svg"), ("Supabase", "supabase-original.svg")]),
    ("Ops", [("AWS", "amazonwebservices-original-wordmark.svg"), ("Docker", "docker-original.svg"),
             ("Nginx", "nginx-original.svg"), ("GPU inference", "nvidia.svg"), ("CI/CD", "cicd.png")]),
]

# Tokens from the portfolio's design/DIRECTION.md (cream theme); dark is the same idea inverted.
THEMES = {
    "light": dict(card="#FFFFFF", bar="#FDF7C4", ink="#161616", muted="#5E5E5C", border="#161616",
                  shadow="#161616", accent="#FACC00", chip="#FFFFFF", cursor="#161616"),
    "dark": dict(card="#161616", bar="#24231F", ink="#F7F5EE", muted="#B4B2AA", border="#F7F5EE",
                 shadow="#FACC00", accent="#FACC00", chip="#1E1E1C", cursor="#FACC00"),
}
ACCENT_INK = "#161616"
EASE = "cubic-bezier(0.16, 1, 0.3, 1)"

# ---------------------------------------------------------------- font

def instance(weight, text):
    font = instantiateVariableFont(TTFont(SRC / "space-grotesk-latin.woff2"), {"wght": weight})
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    adv = {ch: hmtx[cmap[ord(ch)]][0] for ch in set(text) if ord(ch) in cmap}
    missing = set(text) - set(adv)
    assert not missing, f"glyphs missing from font: {missing}"
    sub = subset.Subsetter(subset.Options())
    sub.populate(text=text)
    sub.subset(font)
    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    return adv, base64.b64encode(buf.getvalue()).decode()


class Fonts:
    def __init__(self, text500, text700=""):
        self.adv = {}
        self.faces = []
        for w, text in ((500, text500), (700, text700)):
            if not text:
                continue
            self.adv[w], b64 = instance(w, text)
            self.faces.append(f"@font-face{{font-family:SG;font-weight:{w};"
                              f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")

    def width(self, text, size, weight=500, tracking=0.0):
        return sum(self.adv[weight][c] for c in text) * size / 1000 + tracking * size * len(text)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- header

def header(t, fonts):
    W, H = 840, 236
    cx, cy, cw, ch = 2, 2, 828, 224  # card; hard shadow adds 6px
    bar_h = 36
    x0 = 34
    css, body = [], []

    # Typing line: a card-coloured cover slides right one glyph at a time, carrying the cursor.
    size, ty = 17, 196
    tx = x0 + fonts.width("$ ", size)
    slot, type_t, hold, erase_t = 5.0, 1.9, 2.3, 0.5
    total = slot * len(PHRASES)
    widest = max(fonts.width(p, size) for p in PHRASES)
    lines = []
    for i, p in enumerate(PHRASES):
        stops, x = [], 0.0
        steps = [0.0]
        for c in p:
            x += fonts.width(c, size)
            steps.append(x)
        n = len(p)
        for k, xs in enumerate(steps):  # type
            stops.append((type_t * k / n, xs))
        for k, xs in enumerate(reversed(steps)):  # hold, then backspace
            stops.append((type_t + hold + erase_t * k / n, xs))
        kf = "".join(f"{s / total * 100:.3f}%{{transform:translateX({xs:.2f}px)}}" for s, xs in stops)
        css.append(f"@keyframes t{i}{{{kf}100%{{transform:translateX(0)}}}}")
        shown = slot / total * 100
        css.append(f"@keyframes v{i}{{0%,{shown - 0.01:.3f}%{{opacity:1}}{shown:.3f}%,100%{{opacity:0}}}}")
        css.append(f".p{i}{{opacity:0;animation:v{i} {total}s step-end {i * slot}s infinite}}"
                   f".p{i} .cv{{animation:t{i} {total}s step-end {i * slot}s infinite}}")
        lines.append(
            f'<g class="p{i}"><text x="{tx:.2f}" y="{ty}" class="ty">{esc(p)}</text>'
            f'<g class="cv"><rect x="{tx:.2f}" y="{ty - 18}" width="{widest + 24:.0f}" height="26" fill="{t["card"]}"/>'
            f'<rect class="cur" x="{tx + 1:.2f}" y="{ty - 16}" width="2.5" height="20" fill="{t["cursor"]}"/></g></g>')

    # Pipeline: a dot runs query -> answer; each stage lights up as it passes.
    psize, ph, pgap = 12, 26, 16
    pw = max(fonts.width(s.upper(), psize, 500, 0.04) for s in PIPELINE) + 28
    px = cx + cw - 34 - pw
    py0 = cy + bar_h + (ch - bar_h - (len(PIPELINE) * ph + (len(PIPELINE) - 1) * pgap)) / 2
    lx = px + pw / 2
    cyc = 4.0
    pipe = [f'<line x1="{lx}" y1="{py0 + ph}" x2="{lx}" y2="{py0 + (len(PIPELINE) - 1) * (ph + pgap)}" '
            f'stroke="{t["border"]}" stroke-width="2" stroke-dasharray="3 4"/>']
    for i, s in enumerate(PIPELINE):
        y = py0 + i * (ph + pgap)
        at = (0.08 + i * 0.22) * 100
        on0, on1 = max(at - 2, 0), min(at + 12, 99)
        css.append(f"@keyframes s{i}{{0%,{on0:.1f}%{{fill:{t['chip']}}}{on0 + 2:.1f}%,{on1:.1f}%"
                   f"{{fill:{t['accent']}}}{on1 + 4:.1f}%,100%{{fill:{t['chip']}}}}}"
                   f"@keyframes l{i}{{0%,{on0:.1f}%{{fill:{t['ink']}}}{on0 + 2:.1f}%,{on1:.1f}%"
                   f"{{fill:{ACCENT_INK}}}{on1 + 4:.1f}%,100%{{fill:{t['ink']}}}}}"
                   f".s{i}{{animation:s{i} {cyc}s linear infinite}}.l{i}{{animation:l{i} {cyc}s linear infinite}}")
        pipe.append(f'<rect x="{px + 3}" y="{y + 3}" width="{pw}" height="{ph}" rx="8" fill="{t["shadow"]}"/>'
                    f'<rect class="s{i}" x="{px}" y="{y}" width="{pw}" height="{ph}" rx="8" fill="{t["chip"]}" '
                    f'stroke="{t["border"]}" stroke-width="2"/>'
                    f'<text class="lb l{i}" x="{lx}" y="{y + ph / 2 + 4.2}" text-anchor="middle">{esc(s.upper())}</text>')
    stops = []
    for i in range(len(PIPELINE)):
        y = py0 + i * (ph + pgap) + ph / 2
        stops.append(f"{(0.08 + i * 0.22) * 100:.1f}%{{transform:translateY({y:.1f}px);opacity:1}}")
    css.append(f"@keyframes dot{{0%{{transform:translateY({py0 + ph / 2:.1f}px);opacity:0}}"
               f"6%{{opacity:1}}{''.join(stops)}90%{{transform:translateY({py0 + (len(PIPELINE) - 1) * (ph + pgap) + ph / 2:.1f}px);opacity:0}}"
               f"100%{{opacity:0}}}}.dot{{animation:dot {cyc}s {EASE} infinite}}")

    role_w = fonts.width(ROLE, 23, 700)
    css.append(f"@keyframes hl{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}"
               f".hl{{transform-origin:{x0 - 6}px 0;transform-box:view-box;animation:hl .9s {EASE} .3s both}}"
               f"@keyframes rc{{from{{fill:{t['ink']}}}to{{fill:{ACCENT_INK}}}}}.rl{{animation:rc .3s linear .45s both}}"
               "@keyframes bl{0%,49%{opacity:1}50%,100%{opacity:0}}.cur{animation:bl 1s step-end infinite}"
               "@media (prefers-reduced-motion:reduce){*{animation:none!important}"
               ".p0{opacity:1}.p0 .cv{transform:translateX(9999px)}}")

    style = (f"{''.join(fonts.faces)}text{{font-family:SG,'Space Grotesk','Segoe UI',Helvetica,Arial,sans-serif}}"
             f".nm{{font-size:52px;font-weight:700;letter-spacing:-0.02em;fill:{t['ink']}}}"
             f".rl{{font-size:23px;font-weight:700;letter-spacing:-0.005em;fill:{ACCENT_INK}}}"
             f".pl{{font-size:23px;font-weight:500;fill:{t['muted']}}}"
             f".ty{{font-size:{size}px;font-weight:500;fill:{t['ink']}}}"
             f".pr{{font-size:{size}px;font-weight:500;fill:{t['muted']}}}"
             f".lb{{font-size:{psize}px;font-weight:500;letter-spacing:0.04em;fill:{t['ink']}}}"
             f".bt{{font-size:12px;font-weight:500;letter-spacing:0.04em;fill:{t['muted']}}}" + "".join(css))

    dots = "".join(f'<circle cx="{cx + 22 + k * 20}" cy="{cy + bar_h / 2}" r="6" fill="{f}" stroke="{t["border"]}" stroke-width="1.5"/>'
                   for k, f in enumerate([t["accent"], t["card"], t["card"]]))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title">
<title id="title">{esc(NAME)}, {esc(ROLE)}, {esc(PLACE)}</title>
<style>{style}</style>
<defs><clipPath id="card"><rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="12"/></clipPath>
<clipPath id="tyc"><rect x="{x0}" y="{ty - 22}" width="{px - x0 - 24:.0f}" height="34"/></clipPath></defs>
<rect x="{cx + 6}" y="{cy + 6}" width="{cw}" height="{ch}" rx="12" fill="{t['shadow']}"/>
<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="12" fill="{t['card']}"/>
<rect x="{cx}" y="{cy}" width="{cw}" height="{bar_h}" fill="{t['bar']}" clip-path="url(#card)"/>
<line x1="{cx}" y1="{cy + bar_h}" x2="{cx + cw}" y2="{cy + bar_h}" stroke="{t['border']}" stroke-width="2"/>
<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="12" fill="none" stroke="{t['border']}" stroke-width="2"/>
{dots}<text class="bt" x="{cx + cw / 2}" y="{cy + bar_h / 2 + 4}" text-anchor="middle">{esc(BAR.upper())}</text>
<text class="nm" x="{x0 - 2}" y="{cy + bar_h + 70}">{esc(NAME)}</text>
<rect class="hl" x="{x0 - 6}" y="{cy + bar_h + 90}" width="{role_w + 12:.1f}" height="32" rx="4" fill="{t['accent']}"/>
<text class="rl" x="{x0}" y="{cy + bar_h + 114}">{esc(ROLE)}</text>
<text class="pl" x="{x0 + role_w + 18:.1f}" y="{cy + bar_h + 114}">· {esc(PLACE)}</text>
<text class="pr" x="{x0}" y="{ty}">$</text>
<g clip-path="url(#tyc)">{''.join(lines)}</g>
{''.join(pipe)}
<circle class="dot" cx="{px - 14}" cy="0" r="5" fill="{t['accent']}" stroke="{t['border']}" stroke-width="2"/>
</svg>
"""


# ---------------------------------------------------------------- stack

def data_uri(file):
    raw = (SRC / "logos" / file).read_bytes()
    mime = "image/svg+xml" if file.endswith(".svg") else "image/png"
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


def stack(t, fonts):
    W = 840
    label_w, x_start, right = 112, 118, W - 6
    chip_h, tile, gx, gy, row_gap, fs = 36, 24, 10, 12, 20, 14
    out, y = [], 4
    for label, tools in STACK:
        out.append(f'<text class="cat" x="2" y="{y + chip_h / 2 + 4}">{esc(label.upper())}</text>')
        x = x_start
        for name, logo in tools:
            w = 7 + tile + 9 + fonts.width(name, fs) + 13
            if x + w > right:
                x, y = x_start, y + chip_h + gy
            out.append(f'<rect x="{x + 3}" y="{y + 3}" width="{w:.1f}" height="{chip_h}" rx="8" fill="{t["shadow"]}"/>'
                       f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{chip_h}" rx="8" fill="{t["chip"]}" stroke="{t["border"]}" stroke-width="2"/>')
            tx, ty = x + 7, y + (chip_h - tile) / 2
            if logo:
                out.append(f'<rect x="{tx}" y="{ty}" width="{tile}" height="{tile}" rx="6" fill="#FFFFFF"/>'
                           f'<image x="{tx + 3}" y="{ty + 3}" width="{tile - 6}" height="{tile - 6}" '
                           f'xlink:href="{data_uri(logo)}" preserveAspectRatio="xMidYMid meet"/>')
            else:
                c = tile / 2
                out.append(f'<rect x="{tx}" y="{ty}" width="{tile}" height="{tile}" rx="6" fill="{t["bar"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
                           f'<rect x="{tx + c - 3.5}" y="{ty + c - 3.5}" width="7" height="7" fill="{t["ink"]}" '
                           f'transform="rotate(45 {tx + c} {ty + c})"/>')
            out.append(f'<text class="nm" x="{tx + tile + 9}" y="{y + chip_h / 2 + 5}">{esc(name)}</text>')
            x += w + gx
        y += chip_h + row_gap
    H = int(y - row_gap + 6)
    alt = "; ".join(f"{l}: " + ", ".join(n for n, _ in tl) for l, tl in STACK)
    style = (f"{''.join(fonts.faces)}text{{font-family:SG,'Space Grotesk','Segoe UI',Helvetica,Arial,sans-serif;font-weight:500}}"
             f".cat{{font-size:12px;letter-spacing:0.04em;fill:{t['muted']}}}.nm{{font-size:{fs}px;fill:{t['ink']}}}")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title">
<title id="title">{esc(alt)}</title>
<style>{style}</style>
{''.join(out)}
</svg>
"""


def main():
    head_text = NAME + ROLE + PLACE + "· $" + "".join(PHRASES) + BAR.upper() + "".join(PIPELINE).upper()
    stack_text = "".join(l.upper() for l, _ in STACK) + "".join(n for _, tl in STACK for n, _ in tl)
    hf = Fonts(text500=head_text, text700=NAME + ROLE)
    sf = Fonts(text500=stack_text)
    for name, t in THEMES.items():
        (OUT / f"header-{name}.svg").write_text(header(t, hf), encoding="utf-8")
        (OUT / f"stack-{name}.svg").write_text(stack(t, sf), encoding="utf-8")
        print("wrote", f"header-{name}.svg", f"stack-{name}.svg")


if __name__ == "__main__":
    main()
