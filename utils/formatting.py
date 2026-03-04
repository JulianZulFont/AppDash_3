# utils/formatting.py - Formatting helpers

import numpy as np


def fmt_k(x):
    try:
        if x == 0:
            return "0.00k"
        return f"{float(x):,.2f}k"
    except Exception:
        return "—"


def fmt_pct(x):
    try:
        return f"{float(x):,.1f}%"
    except Exception:
        return "—"


def _fmt_money(x):
    """Format as money with commas."""
    try:
        return f"{float(x):,.2f}"
    except Exception:
        return ""


def _r2(y_true, y_pred):
    """Calcular R^2 simple manual."""
    try:
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        if ss_tot == 0:
            return 0.0
        return float(1 - ss_res / ss_tot)
    except Exception:
        return 0.0
