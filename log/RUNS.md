# RUNS — Kaggle koşu kuyruğu

Kodu insana vermeden önce `python tools/kx.py board` bak.

| slug | kim | başlangıç | GPU? | tahmini bitiş | durum |
|---|---|---|---|---|---|
| | | | | | |

## Kurallar
- GPU gerektirmeyen her şey **CPU'da koşar** (tablo/GBDT dahil). GPU kotası derin
  öğrenmeye ve uzun FULL koşulara saklanır.
- Eşzamanlı koşu limiti hesap başınadır ve GPU tarafında dardır.
  **Gerçek limiti Cuma 11:00 provasında ölç**, `case/CASE.md`'ye yaz, varsayma.
- Kalan GPU kotası Cuma 11:00'de ve her `/durum` turunda kontrol edilir, `STATUS.md`'ye yazılır.
- Hesap paylaşılıyorsa notebook adı da paylaşılır: `as-cl-exp-xxx` / `as-cx-exp-2xx`
  dışına çıkma, var olan bir adın üstüne koşma.
