# AGENTS.md

Proje kuralları `CLAUDE.md`'dedir. Önce onu oku.

Codex için ek: çağrı protokolü, kimlik ayrımı ve çıktı formatları `CODEX.md`'dedir.
Sana verilen görev beş çağrı tipinden biridir; o tipin istenen çıktı formatının dışına çıkma.

Kısa hatırlatma:
- Codex deneyleri `EXP-2xx`, Kaggle notebook adı `as-cx-exp-2xx`, klasör `experiments/EXP-2xx/`.
- Merkezi dosyaları (`STATUS.md`, `log/BACKLOG.md`, `experiments/EXP_SUMMARY.md`,
  `case/CASE.md`) değiştirme. Sonucu yapılandırılmış döndür, merkezi kayda Claude işler.
- Ölçülmemiş skor etkisini sayı olarak verme.
- **Kaggle'a hiçbir şey gönderme** — ne notebook, ne dataset, ne submission. Koşuyu
  insan yapar: kod `experiments/EXP-2xx/code.py`'ye yazılır, insan Kaggle'a yapıştırır.
- Fold ve metrik `core/folds_snippet.py` + `core/metric.py`'den **aynen** gömülür; kod
  kendi fold'unu üretmez. Koşu fold parmak izini basar, tutmazsa sonuç kayda girmez.

**Çağrı 4 (fikir üretimi) zorunlu bir adımdır, opsiyonel değil.** İlk baseline sonucu
gelir gelmez, Claude başka deney açmadan önce bu çağrıyı yapar (`CLAUDE.md` →
"Baseline'dan hemen sonra: liste zorunlu"). Bu çağrı geldiğinde en fazla 3 fikir,
her biri dayanak + uygulanacak değişiklik + tahmini süre ile — ders kitabı cevabı değil,
verilen case/TRAPS/baseline bulgularına gömülü, verilen bütçeye göre somut fikirler.
