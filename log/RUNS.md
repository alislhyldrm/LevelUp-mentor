# RUNS — Kaggle koşu kuyruğu

Kodu insana vermeden önce `python tools/kx.py board` bak.

> D-02: koşu Kaggle'da değil, **Colab'da ajan tarafından** yapılıyor. Kaggle'a gönderim yok (K-01).

| slug | kim | başlangıç | GPU | tahmini bitiş | durum |
|---|---|---|---|---|---|
| EXP-001_smoke | Claude/Colab | 25 Eyl | T4 | — | **bitti** — 2/2 epoch, 2:05. Boru hattı testi; skor karşılaştırmasına girmez |
| EXP-001 (T4, iptal) | Claude/Colab | 25 Eyl | T4 | — | **iptal** — 1 epoch (AP50 0,0077), 28 dk/ep = 28 sa, sığmadı. Arşiv: `EXP-001_t4_kismi_2149` |
| EXP-001 (tam) | Claude/Colab | 26 Eyl | **A100-80GB** | **4,5 sa** (60 ep × 4,5 dk, ölçüldü) | **koşuyor** |

## Kurallar
- GPU gerektirmeyen her şey **CPU'da koşar** (tablo/GBDT dahil). GPU kotası derin
  öğrenmeye ve uzun FULL koşulara saklanır.
- Eşzamanlı koşu limiti hesap başınadır ve GPU tarafında dardır.
  **Gerçek limiti Cuma 11:00 provasında ölç**, `case/CASE.md`'ye yaz, varsayma.
- Kalan GPU kotası Cuma 11:00'de ve her `/durum` turunda kontrol edilir, `STATUS.md`'ye yazılır.
- Hesap paylaşılıyorsa notebook adı da paylaşılır: `as-cl-exp-xxx` / `as-cx-exp-2xx`
  dışına çıkma, var olan bir adın üstüne koşma.
