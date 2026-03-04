# components/common.py - Reusable UI Components

from dash import html
from styles import STYLES
from theme import COLORS


def stat_card(title, rows, note=None):
    """rows: list of (label, value)"""
    return html.Div(
        [
            html.Div(title, style={"fontWeight": "700",
                     "marginBottom": "0.6rem"}),
            html.Table(
                [html.Tbody([html.Tr([
                    html.Td(k, style={"paddingRight": "1rem",
                            "color": COLORS["on-surface-variant"]}),
                    html.Td(v)
                ]) for k, v in rows])],
                style={"width": "100%", "borderCollapse": "collapse",
                       "fontSize": "0.95rem"},
            ),
            html.Div(note, style={
                "marginTop": "0.6rem", "color": COLORS["on-surface-variant"], "fontSize": "0.9rem"
            }) if note else None,
        ],
        style={
            **STYLES["card"],
            "marginTop": "1rem",
            "padding": "1rem 1.1rem",
        },
    )


def tab_block(title: str, subtitle: str, children):
    """Bloque estándar para cada pestaña: encabezado + contenido."""
    return html.Div(
        [
            html.Div(
                [
                    html.H2(title, style={
                            "margin": "0 0 0.25rem 0", "fontFamily": "'Montserrat', sans-serif"}),
                    html.P(subtitle, style={
                           "margin": "0 0 1rem 0", "color": COLORS["on-surface-variant"]}),
                ],
                style={"marginBottom": "0.5rem"},
            ),
            *children,
        ]
    )


def card(children, style=None):
    base_style = {
        "backgroundColor": "#1e1e1e",
        "padding": "20px",
        "borderRadius": "12px",
        "marginBottom": "20px",
        "boxShadow": "0 2px 10px rgba(0,0,0,0.2)"
    }
    if style:
        base_style.update(style)
    return html.Div(children, style=base_style)


def stat_box(title, stats, columns=2):
    """Grid of statistics inside a card."""
    pairs = []
    if isinstance(stats, dict):
        pairs = list(stats.items())
    elif isinstance(stats, list):
        if len(stats) > 0 and isinstance(stats[0], (list, tuple)) and len(stats[0]) == 2:
            pairs = [(str(k), v) for k, v in stats]
        elif len(stats) > 0 and isinstance(stats[0], dict):
            for d in stats:
                k = d.get("label") or d.get("k") or d.get("name") or "Dato"
                v = d.get("value") or d.get("v") or d.get("val") or ""
                pairs.append((str(k), v))
        else:
            pairs = [(f"Dato {i+1}", v) for i, v in enumerate(stats)]
    else:
        pairs = [("Valor", stats)]

    items = []
    for k, v in pairs:
        items.append(
            html.Div(
                [
                    html.Div(k, style=STYLES.get("stat_label", {
                             "fontSize": "12px", "opacity": 0.75})),
                    html.Div(str(v), style=STYLES.get("stat_value", {
                             "fontSize": "18px", "fontWeight": "700"})),
                ],
                style={"padding": "8px 10px"}
            )
        )

    grid_style = {
        "display": "grid",
        "gridTemplateColumns": f"repeat({columns}, minmax(0, 1fr))",
        "gap": "6px",
        "marginTop": "10px"
    }

    return card(
        [
            html.Div(title, style=STYLES.get(
                "h3", {"fontSize": "16px", "fontWeight": "700"})),
            html.Div(items, style=grid_style)
        ],
        style=STYLES.get("stat_card", {})
    )
