"""Resmi metrik. /case bunu yarismanin Evaluation sayfasindan yazar.
Tek sozlesme: score(y_true, y_pred) -> float  +  GREATER_IS_BETTER
Butun notebook'lar bunu hackathon-core dataset'inden okur, kendisi yazmaz.
"""
import numpy as np

GREATER_IS_BETTER = True


def score(y_true, y_pred) -> float:
    """SABLON: ROC AUC (saf numpy). Case gelince resmi metrikle degistir."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    order = np.argsort(y_pred)
    ranks = np.empty(len(y_pred), dtype=float)
    ranks[order] = np.arange(1, len(y_pred) + 1)
    # esit degerlere ortalama rank
    s = np.sort(y_pred)
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + j + 2) / 2
        i = j + 1
    n_pos = int((y_true == 1).sum())
    n_neg = len(y_true) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    return float((ranks[y_true == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))
