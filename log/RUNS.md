# RUNS — Kaggle koşu kuyruğu

Push etmeden önce `python tools/kx.py board` bak.

| slug | kim | başlangıç | GPU? | tahmini bitiş | durum |
|---|---|---|---|---|---|
| | | | | | |

## Kurallar
- GPU gerektirmeyen her şey **CPU'da koşar** (tablo/GBDT dahil). GPU kotası derin
  öğrenmeye ve gece koşularına saklanır.
- Eşzamanlı koşu limiti hesap başınadır ve GPU tarafında dardır.
  **Gerçek limiti Cuma 11:00 provasında ölç**, `case/CASE.md`'ye yaz, varsayma.
- Kalan GPU kotası Cuma 11:00'de ve gece 00:00'da kontrol edilir, `STATUS.md`'ye yazılır.
- Hesap paylaşılıyorsa slug namespace'i de paylaşılır: `as-cl-exp-xxx` / `as-cx-exp-2xx`
  dışına çıkma, var olan slug'a push etmeden önce kimliğini doğrula.
