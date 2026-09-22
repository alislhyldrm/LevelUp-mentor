# AGENTS.md

Proje kuralları `CLAUDE.md`'dedir. Önce onu oku.

Codex için ek: çağrı protokolü, kimlik ayrımı ve çıktı formatları `CODEX.md`'dedir.
Sana verilen görev beş çağrı tipinden biridir; o tipin istenen çıktı formatının dışına çıkma.

Kısa hatırlatma:
- Codex deneyleri `EXP-2xx`, kernel slug `as-cx-exp-2xx`, klasör `experiments/EXP-2xx/`.
- Merkezi dosyaları (`STATUS.md`, `log/BACKLOG.md`, `experiments/EXP_SUMMARY.md`,
  `case/CASE.md`) değiştirme. Sonucu yapılandırılmış döndür, merkezi kayda Claude işler.
- Ölçülmemiş skor etkisini sayı olarak verme.
- Kaggle'a submit etme.

**Çağrı 4 (fikir üretimi) zorunlu bir adımdır, opsiyonel değil.** İlk baseline sonucu
gelir gelmez, Claude başka deney açmadan önce bu çağrıyı yapar (`CLAUDE.md` →
"Baseline'dan hemen sonra: liste zorunlu"). Bu çağrı geldiğinde en fazla 3 fikir,
her biri dayanak + uygulanacak değişiklik + tahmini süre ile — ders kitabı cevabı değil,
verilen case/TRAPS/baseline bulgularına gömülü, verilen bütçeye göre somut fikirler.
