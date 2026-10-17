"""Generate the animated terminal header SVGs for the GitHub profile README.

Run: python scripts/build_terminal.py

Two variants are written: assets/terminal-dark.svg and assets/terminal-light.svg.
The README picks one with <picture> + prefers-color-scheme, and the last command's
output differs between them (one of the easter eggs).

Animation is pure SMIL (<set>/<animate>), which GitHub's image proxy allows and
which Chrome, Firefox and Safari all play inside <img>. No scripts, no web fonts.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": {
        "bg": "#0d1117", "panel": "#161b22", "border": "#30363d",
        "text": "#e6edf3", "dim": "#8b949e", "green": "#3fb950",
        "blue": "#58a6ff", "accent": "#d2a8ff",
        "theme_line": "dark mode. respect.",
    },
    "light": {
        "bg": "#ffffff", "panel": "#f6f8fa", "border": "#d0d7de",
        "text": "#1f2328", "dim": "#656d76", "green": "#1a7f37",
        "blue": "#0969da", "accent": "#8250df",
        "theme_line": "light mode?! bold. respect anyway.",
    },
}

W = 860
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
FS = 17
LH = 31
TOP = 72          # baseline of first line
LEFT = 28
CHAR_S = 0.065    # typing speed, seconds per character


def hidden(content: str, at: float, cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return (f'<tspan{c} visibility="hidden">'
            f'<set attributeName="visibility" to="visible" begin="{at:.2f}s" fill="freeze"/>'
            f'{escape(content)}</tspan>')


def prompt(at: float) -> str:
    return (hidden("imre@antwerp", at, "g") + hidden(":", at) +
            hidden("~", at, "b") + hidden("$ ", at))


def typed(cmd: str, start: float) -> tuple[str, float]:
    parts, t = [], start
    for ch in cmd:
        parts.append(hidden(ch, t))
        t += CHAR_S
    return "".join(parts), t


def build(name: str, th: dict) -> str:
    script = [
        ("cmd", "whoami"),
        ("out", [("Imre Czidor", ""), ("  ·  business student who ships software", "d")]),
        ("cmd", "ls ./building"),
        ("out", [("web-apps/   self-hosted-tools/   ai-automations/", "b")]),
        ("cmd", "echo $THEME"),
        ("out", [(th["theme_line"], "a")]),
        ("end", None),
    ]

    lines, t = [], 0.4
    for i, (kind, payload) in enumerate(script):
        y = TOP + i * LH
        if kind == "cmd":
            p = prompt(t)
            body, t_end = typed(payload, t + 0.35)
            lines.append(f'<text x="{LEFT}" y="{y}" xml:space="preserve">{p}{body}</text>')
            t = t_end + 0.3
        elif kind == "out":
            spans = "".join(hidden(txt, t, cls) for txt, cls in payload)
            lines.append(f'<text x="{LEFT}" y="{y}" xml:space="preserve">{spans}</text>')
            t += 0.45
        else:  # final prompt with blinking cursor
            cursor = (f'<tspan class="c" visibility="hidden">'
                      f'<animate attributeName="visibility" values="visible;hidden" '
                      f'dur="1.1s" begin="{t:.2f}s" repeatCount="indefinite" calcMode="discrete"/>'
                      f'█</tspan>')
            lines.append(f'<text x="{LEFT}" y="{y}" xml:space="preserve">{prompt(t)}{cursor}</text>')

    h = TOP + (len(script) - 1) * LH + 30
    dots = "".join(
        f'<circle cx="{28 + k * 22}" cy="22" r="6.5" fill="{c}"/>'
        for k, c in enumerate(["#ff5f57", "#febc2e", "#28c840"])
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="Terminal: whoami, Imre Czidor, business student who ships software">
<title>imre@antwerp: ~</title>
<style>
  text {{ font-family: {FONT}; font-size: {FS}px; fill: {th["text"]}; white-space: pre; }}
  .g {{ fill: {th["green"]}; font-weight: 600; }}
  .b {{ fill: {th["blue"]}; }}
  .d {{ fill: {th["dim"]}; }}
  .a {{ fill: {th["accent"]}; font-style: italic; }}
  .c {{ fill: {th["text"]}; }}
  .t {{ font-size: 13px; fill: {th["dim"]}; }}
</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="12" fill="{th["panel"]}" stroke="{th["border"]}"/>
<path d="M0.5 44 H{W - 0.5}" stroke="{th["border"]}"/>
{dots}
<text class="t" x="{W / 2}" y="27" text-anchor="middle">imre@antwerp: ~</text>
{chr(10).join(lines)}
</svg>
'''


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, th in THEMES.items():
        (OUT / f"terminal-{name}.svg").write_text(build(name, th), encoding="utf-8")
        print("wrote", OUT / f"terminal-{name}.svg")


if __name__ == "__main__":
    main()
