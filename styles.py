from theme import COLORS

STYLES = {
    "container": {
        "backgroundColor": COLORS["background"],
        "color": COLORS["on-background"],
        "minHeight": "100vh",
        "padding": "2rem",
        "fontFamily": "'Inter', sans-serif",
    },
    "card": {
        "backgroundColor": COLORS["card"],
        "backdropFilter": "blur(10px)",
        "borderRadius": "16px",
        "padding": "1.25rem",
        "border": "1px solid rgba(255, 255, 255, 0.1)",
        "boxShadow": "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        "marginBottom": "1.25rem",
    },
    "title": {
        "fontFamily": "Montserrat",
        "fontWeight": "800",
        "color": COLORS["primary"],
        "marginBottom": "0.25rem",
        "fontSize": "2.2rem",
        "letterSpacing": "-1px",
    },
    "subtitle": {
        "color": COLORS["on-surface-variant"],
        "marginBottom": "1.25rem",
        "fontSize": "1.1rem",
        "fontWeight": "400",
        "maxWidth": "80%",
        "lineHeight": "1.6",
    },
    "label": {
        "color": COLORS["on-background"],
        "marginBottom": "0.6rem",
        "display": "block",
        "fontWeight": "600",
        "fontSize": "0.85rem",
        "textTransform": "uppercase",
        "letterSpacing": "1px",
    },
    "h3": {
        "margin": "0 0 10px 0",
        "fontFamily": "Montserrat",
        "fontSize": "18px",
        "fontWeight": "700",
    },
    "p": {
        "margin": "0 0 12px 0",
        "opacity": 0.9,
        "lineHeight": "1.5",
        "fontSize": "14px",
    },
    "note": {
        "marginTop": "8px",
        "fontSize": "12px",
        "opacity": 0.8,
        "lineHeight": "1.4"
    },
    "dropdown": {
        "maxWidth": "520px",
        "marginTop": "1.5rem",
        "marginBottom": "1rem",
    }
}
