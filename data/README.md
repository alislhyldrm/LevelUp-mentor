# data/ — yarışma verisi

**Aşama:** 1, triyajdan hemen sonra. `kaggle competitions download -c <slug>` ile iner.
403 alınırsa yarışma kurallarının siteden kabul edilmesi gerekir (insan yapar).

**İçerik:** `train.csv`, `test.csv`, `sample_submission.csv` ve yarışmanın verdiği
diğer dosyalar. Repoya commit edilmez (büyük); makinede durur.

**Kim yazar:** Kaggle'dan indirilir, elle düzenlenmez.

**Nerede kullanılır:** yerel EDA, `tools/make_folds.py`, ve `submission.csv` format
kontrolünün referansı (`sample_submission.csv` — `kx.json`'daki `sample_submission`).

**Ne zaman sabitlenir:** yarışma yeni sürüm yayınlamadıkça değişmez. Değişirse
`core/cv_spec.md` sürümlenir.
