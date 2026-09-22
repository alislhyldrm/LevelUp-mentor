# core/ — CV sözleşmesi

**Aşama:** 1 sonu, D-01 (CV + metrik onayı) alındıktan hemen sonra.

| Dosya | Ne işe yarar | Kim yazar |
|---|---|---|
| `folds_snippet.py` | Fold üretim kodu + parmak izi fonksiyonu. **Tek doğruluk kaynağı** | ajan, D-01'e göre |
| `folds.csv` | `id, fold, y` — `python tools/make_folds.py` üretir | araç |
| `metric.py` | `score(y_true, y_pred)` + `GREATER_IS_BETTER` | ajan, Evaluation sayfasından |
| `cv_spec.md` | Ana şema, ana skor, FAST tanımı, fold parmak izi | ajan, insan onaylar |

**Kaggle'a yüklenmez.** Koşuda fold ve metrik bu dosyaların metni `code.py`'ye **aynen
gömülerek** uygulanır. Garanti dosya paylaşımı değil, **fold parmak izi eşitliğidir**;
tutmayan koşu kayda girmez.

**Ne zaman sabitlenir:** D-01'den sonra. Sadece kanıtlanmış bir kusur (sızıntı, gruplama
ihlali) için değişir; değişirse yeni CV sürümü açılır ve eski skorlar aynı tabloda
karşılaştırılmaz (`CLAUDE.md` kural 1).
