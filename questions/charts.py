"""Draw the report's charts as plain SVG files, one for GitHub's light theme and one for its dark theme.

No libraries. Three forms, all horizontal bars with the value printed at the bar's end:
  bars     one bar per row
  grouped  two or more named series per row, with a legend
  part_of  a part drawn inside its whole ("2 of 4")
Colors are the first two slots of a validated categorical palette (blue, orange), checked for color-blind
separation and contrast against GitHub's light and dark backgrounds.
"""
import os
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARTS = os.path.join(ROOT, "charts")
THEMES = {
    "light": {"ink": "#0b0b0b", "ink2": "#52514e", "muted": "#898781", "track": "#ebeae4", "context": "#c3c2b7",
              "series": ["#2a78d6", "#eb6834"]},
    "dark": {"ink": "#f0efec", "ink2": "#c3c2b7", "muted": "#898781", "track": "#2c2c2a", "context": "#5b5a55",
             "series": ["#3987e5", "#d95926"]},
}
WIDTH = 760
BAR_AREA = 430   # widest a bar may be; the rest of the width is room for the value and note printed after it
BAR = 10
FONT = 'font-family="system-ui, -apple-system, Segoe UI, sans-serif"'


def number(value):
    if isinstance(value, float) and value == int(value):
        value = int(value)
    return f"{value:,}" if isinstance(value, int) else str(value)


def bar(x, y, width, color):
    """A thin bar anchored at the left, rounded at its data end."""
    width = max(width, 0)
    if width < 5:
        return f'<rect x="{x}" y="{y}" width="{max(width, 2 if width else 0):.1f}" height="{BAR}" fill="{color}"/>'
    end = x + width
    return (f'<path d="M{x},{y} H{end - 4:.1f} Q{end:.1f},{y} {end:.1f},{y + 4} V{y + BAR - 4} '
            f'Q{end:.1f},{y + BAR} {end - 4:.1f},{y + BAR} H{x} Z" fill="{color}"/>')


def text(x, y, content, color, size=13, weight="400", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" {FONT}>{escape(content)}</text>')


def write(stem, title, height, body):
    os.makedirs(CHARTS, exist_ok=True)
    for theme, colors in THEMES.items():
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
                 f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="{escape(title)}">',
                 f"<title>{escape(title)}</title>"]
        parts += body(colors)
        parts.append("</svg>")
        with open(os.path.join(CHARTS, f"{stem}-{theme}.svg"), "w") as handle:
            handle.write("\n".join(parts) + "\n")
    return {"stem": stem, "title": title}


def legend(colors, names, swatches, y):
    out, x = [], 0
    for name, swatch in zip(names, swatches):
        out.append(f'<rect x="{x}" y="{y - 9}" width="10" height="10" rx="2" fill="{swatch}"/>')
        out.append(text(x + 16, y, name, colors["ink2"], 12))
        x += 16 + 7.0 * len(name) + 22
    return out


def bars(stem, title, rows, unit="", top=None, context=(), reference=None):
    """rows: dicts with label, value and optionally note (printed, muted, after the value).
    `context` lists labels drawn in gray: reference rows that are not the subject of the chart.
    `reference` is (value, label): a vertical line across all bars at that value."""
    rows = rows or [{"label": "(no cases in this study)", "value": 0}]
    top = top or max(row["value"] for row in rows) or 1
    head = 18 if reference else 0
    height = 8 + head + 42 * len(rows)

    def body(colors):
        out = []
        if reference:
            x = BAR_AREA * reference[0] / top
            out.append(text(x, 11, reference[1], colors["muted"], 11, anchor="middle"))
            out.append(f'<line x1="{x:.1f}" y1="16" x2="{x:.1f}" y2="{height - 4}" stroke="{colors["muted"]}" '
                       f'stroke-width="1" stroke-dasharray="3 3"/>')
        for i, row in enumerate(rows):
            y = head + 16 + 42 * i
            out.append(text(0, y, row["label"], colors["ink2"]))
            color = colors["context"] if row["label"] in context else colors["series"][0]
            width = BAR_AREA * row["value"] / top
            out.append(f'<rect x="0" y="{y + 8}" width="{BAR_AREA}" height="{BAR}" rx="2" fill="{colors["track"]}"/>')
            out.append(bar(0, y + 8, width, color))
            label = number(row["value"]) + unit
            out.append(text(BAR_AREA + 10, y + 18, label, colors["ink"], 13, "600"))
            if row.get("note"):
                out.append(text(BAR_AREA + 10 + 8.2 * len(label) + 8, y + 18, row["note"], colors["muted"], 12))
        return out
    return write(stem, title, height, body)


def grouped(stem, title, labels, series, unit="", top=None):
    """series: list of (name, values aligned with labels). A value of None draws no bar for that series."""
    top = top or max(v for _, values in series for v in values if v is not None) or 1
    pitch = 24 + 22 * len(series) + 10
    height = 30 + pitch * len(labels)

    def body(colors):
        out = legend(colors, [name for name, _ in series], colors["series"], 12)
        for i, label in enumerate(labels):
            y = 44 + pitch * i
            out.append(text(0, y, label, colors["ink"], 13, "600"))
            for j, (name, values) in enumerate(series):
                value = values[i]
                if value is None:
                    continue
                by = y + 8 + 22 * j
                out.append(f'<rect x="0" y="{by}" width="{BAR_AREA}" height="{BAR}" rx="2" fill="{colors["track"]}"/>')
                out.append(bar(0, by, BAR_AREA * value / top, colors["series"][j]))
                out.append(text(BAR_AREA + 10, by + 10, number(value) + unit, colors["ink"], 13, "600"))
                if len(name) <= 24:  # longer names are left to the legend, or they run off the edge
                    out.append(text(BAR_AREA + 10 + 8.2 * len(number(value) + unit) + 8, by + 10, name, colors["muted"], 12))
        return out
    return write(stem, title, height, body)


def part_of(stem, title, rows, part_name, whole_name):
    """rows: dicts with label, part, whole. The whole is drawn in gray with the part in color inside it."""
    top = max(row["whole"] for row in rows) or 1
    height = 30 + 42 * len(rows)

    def body(colors):
        out = legend(colors, [whole_name, part_name], [colors["context"], colors["series"][0]], 12)
        for i, row in enumerate(rows):
            y = 44 + 42 * i
            out.append(text(0, y, row["label"], colors["ink2"]))
            out.append(f'<rect x="0" y="{y + 8}" width="{BAR_AREA}" height="{BAR}" rx="2" fill="{colors["track"]}"/>')
            out.append(bar(0, y + 8, BAR_AREA * row["whole"] / top, colors["context"]))
            out.append(bar(0, y + 8, BAR_AREA * row["part"] / top, colors["series"][0]))
            out.append(text(BAR_AREA + 10, y + 18, f"{number(row['part'])} of {number(row['whole'])}", colors["ink"], 13, "600"))
        return out
    return write(stem, title, height, body)
