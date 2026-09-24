# AGENTS.md

Proje kuralları `CLAUDE.md`'dedir. Önce onu oku. Codex bu repoda iki moddan birinde çalışır:

- **Yardımcı mod** (varsayılan): Claude koordinatördür, sana `CODEX.md` kabıyla çağrı gelir.
- **Koordinatör modu**: insan "Claude yok / limit doldu, devam et" der. Claude'un rolünü
  sen üstlenirsin.

Takım arkadaşlarının kod şartları ve teknik kuralları (sızıntı, CV, HPO, pseudo-label,
ensemble…) her iki modda `SOZLESME.md`'dedir.

## Her iki modda
- **Kaggle'a hiçbir şey gönderme** — ne notebook, ne dataset, ne submission. Koşuyu
  insan yapar: kod `experiments/EXP-xxx/code.py`'ye yazılır, insan inceler, Kaggle'a
  yapıştırır veya yerelde koşturur.
- Fold ve metrik `core/folds_snippet.py` + `core/metric.py`'den **aynen** gömülür; kod
  kendi fold'unu üretmez. Koşu fold parmak izini basar, tutmazsa sonuç kayda girmez.
- Kodu verirken uygulanan teknikleri sohbette de yaz (ne · neden · sızıntı nasıl önlendi);
  aynı satırlar `code.py` içindeki `TEKNIKLER` listesindedir.
- Ölçülmemiş skor etkisini sayı olarak verme.

## Yardımcı mod
Çağrı protokolü, kimlik ayrımı ve çıktı formatları `CODEX.md`'dedir. Görev beş çağrı
tipinden biridir; o tipin istenen çıktı formatında dön.
- Codex deneyleri `EXP-2xx`, Kaggle notebook adı `as-cx-exp-2xx`, klasör `experiments/EXP-2xx/`.
- Merkezi dosyalar (`STATUS.md`, `log/BACKLOG.md`, `experiments/EXP_SUMMARY.md`,
  `case/CASE.md`) Claude'undur. Sonucu yapılandırılmış döndür, merkezi kayda Claude işler.

**Çağrı 4 (fikir üretimi) zorunlu bir adımdır.** İlk baseline sonucu gelir gelmez, Claude
başka deney açmadan önce bu çağrıyı yapar (`CLAUDE.md` → "Baseline'dan hemen sonra: liste
zorunlu"). En fazla 3 fikir, her biri dayanak + uygulanacak değişiklik + tahmini süre ile —
verilen case/TRAPS/baseline bulgularına gömülü, verilen bütçeye göre somut.

## Koordinatör modu
`CLAUDE.md`'de "sen" diye geçen rol artık sensin: merkezi dosyaları sen yazarsın, kayıt,
karşılaştırma ve karar önerisi sende.

1. **İlk iş `STATUS.md`.** Üç satır özetle — buradayız / nerede kalmıştık / insandan
   sıradaki eylem — sonra dur, insanın onayını bekle. Bağlam yalnız bu dosyadan gelir;
   Claude'un sohbet geçmişi sende yok.
2. **Skill'ler prosedürdür.** `/case`, `/exp`, `/final`, `/durum`, `/mentor` sende komut
   değildir; ilgili adımda `.claude/skills/<ad>/SKILL.md` dosyasını oku ve adımlarını
   sırayla uygula.
3. **Numaralama:** yeni deneyler koordinatör serisinden, `EXP_SUMMARY.md`'deki sıradaki
   boş numarayla (`0xx/1xx`) açılır. `card.md`'ye "yazan: codex (koordinatör modu)" satırı
   düşülür. Açık `EXP-2xx` deneylerin olduğu gibi kayda girer.
4. **Araçlar aynı:** `python tools/kx.py new | kayit | cmp | gurultu | board`,
   `tools/blend.py`, `tools/adv_val.py`. Karar `CLAUDE.md` karar kuralı tablosuyla verilir.
5. **Bağımsız ikinci görüş yok.** `CODEX.md` çağrıları (Çağrı 1 validation denetimi,
   Çağrı 4 fikir üretimi) normalde ikinci bir ajanın körlemesine görüşüdür. Kendine
   çağıramazsın: bu adımlarda kendi önerini yaz ve insana "ikinci görüş alınmadı" de.
   Onay 1 / Onay 2 paketinde bu satır görünür.
6. **Devir:** insan "ara veriyorum / kapatıyorum / Claude geri geldi" dediğinde
   `STATUS.md`'yi `CLAUDE.md` kural 8'e göre yeniden yaz; "Bu oturumda ne oldu"nun ilk
   satırı "koordinatör: codex" olur. Claude dönünce oradan devam eder.
