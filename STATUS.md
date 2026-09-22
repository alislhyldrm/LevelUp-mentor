# STATUS — Kaggle Hekaton | Cuma 12:00 → Cumartesi 12:00
<!-- Oturum devir dosyası. Yeni oturum önce bunu okur. Append edilmez, yeniden yazılır. -->

## İnsandan sıradaki eylem
→ Kurulum bitti, prova tamamlandı. Kalan tek şey Cuma 11:00 kontrol listesi
  (aşağıda) — özellikle **hangi Kaggle hesabından koşulacağına karar ver.**

## Şu an
Faz: HAZIRLIK TAMAMLANDI | Ana hat: yok (yarış başlamadı) | Son güncelleme: 22 Eyl
Kaggle'da koşan: yok | Kalan GPU kotası: bilinmiyor | Son FULL başlatma saati: —

## Sıradaki 3 iş
1. Cuma 11:00 kontrol listesini tamamla (aşağıda)
2. Hangi hesaptan koşulacağını netleştir (aktif risk, aşağıda)
3. Cuma 12:00'de `/case` ile başla

## Bu oturumda ne oldu
- Eski çelişen sistem (~/.claude/skills'teki 5 global skill + lokal runner) arşive
  taşındı; proje-içi 5 skill (`case exp mentor durum final`) + `CLAUDE.md` + `CODEX.md`
  + `tools/kx.py` (~330 satır) + `tools/blend.py` + notebook şablonu kuruldu, git'e işlendi.
- **Uçtan uca prova yapıldı** (kişisel Kaggle hesabında, `playground-series-s6e9`,
  geçici klasörde — bkz. plan/HEKATON_FINAL_PLAN_v4.md §13.2). Tam zincir çalıştı:
  case → Codex validation denetimi → core/ (folds+metric) → Kaggle dataset → 2 gerçek
  deney (push→status→fetch→doğrula→cmp) → blend.py.
- **5 gerçek bug bulundu ve düzeltildi** (kalıcı, `tools/kx.py` + `tools/notebook_template.ipynb`'de):
  1. Kernel başlığı slug'a tam dönüşmezse Kaggle sessizce farklı slug üretiyordu →
     başlık artık `= slug`, push sonrası otomatik doğrulama eklendi.
  2. `/kaggle/input/` yolu CLI-push'ta sabit değil (iç içe `competitions/`/`datasets/<owner>/`) →
     şablon artık `rglob` ile otomatik buluyor.
  3. Codex incelemesi: `folds` tam merge hedefi (`y`) FEATURES'a sızdırıyordu + test
     tahmini submission'a pozisyonel atanıyordu → ikisi de şablonda düzeltildi.
  4. Notebook'ta bir syntax hatası Kaggle kuyruğuna girip ~5 dk sonra hata olarak
     döndü → `kx.py push` artık `ast.parse` ile yerel ön kontrol yapıyor.
  5. `kaggle kernels status` "RUNNING" derken koşu gerçekte bitmiş olabiliyordu
     (~19 dk gecikme). `CLAUDE.md` → "Tekrarlanan hatalar"a yazıldı.
- 2 küçük süreç notu da eklendi: sklearn sürüm uyumsuzluğu riski (final kapısı için),
  backlog'u atlayıp doğrudan deney açma riski.
- Prova sonucu: EXP-001 (baseline HGB) cv_oof 0.9397, EXP-002 (kırpma göstergesi
  hipotezi) RED — iki özellik ağaç modelinde tamamen artık çıktı, hem Kaggle'da hem
  yerelde bit-düzeyinde doğrulandı. Karar mekanizması (cmp/blend) doğru çalıştı.

## Önceki oturum
- (kayıt yok)

## Öncesi
- (kayıt yok)

## Sabitlenen kararlar
- D-01 sadece PROVA'da alındı (gerçek case'te değil): CV=StratifiedKFold(5,seed=42),
  metrik=ROC AUC, ana skor=cv_oof. Gerçek hekatonda bu karar case'e göre yeniden verilir.

## Denendi, işe yaramadı
- (gerçek yarışta henüz yok — prova bulguları yukarıda "Bu oturumda ne oldu"da)

## Aktif riskler
- **Kaggle CLI kişisel hesaba (`alisalihyldrm`) bağlı.** Yarışma ortak hesaptan
  koşacaksa token'ın Cuma sabahından önce değiştirilmesi gerekiyor — kullanıcı bunu
  netleştirmedi ("her takımın bir e-postası var, oradan gidecek" dedi ama token henüz
  değiştirilmedi).
- Eşzamanlı koşu limiti ve GPU kotası henüz ölçülmedi (ortak hesapta ölçülmeli).
- Kaggle push→complete arası gerçek gecikme (~19 dk prova'da) FULL koşu zamanlamasına
  eklenmeli; `durum` skill'indeki "son FULL başlatma saati" formülü bunu hesaba katmıyor.

## Nerede kaldım / dikkat
- Prova'nın kendi dosyaları (CASE.md, cv_spec.md, deneyler) **geçici klasörde** kaldı,
  gerçek repoya taşınmadı (kullanıcı talimatı). `case/CASE.md` ve `core/cv_spec.md`
  hâlâ boş şablon — Cuma günü gerçek case ile doldurulacak.
- `tools/blend.py`'nin sıfır-fark edge-case'inde (iki model bit-birebir aynıysa) öneri
  metni "RED" diyor ama "fark zaten yok" diye ayrı belirtmiyor — kozmetik, düzeltilmedi.

## Ürüne taşınabilecek en güçlü 3 bulgu
1. —  2. —  3. —

## Cuma 11:00 kontrol listesi
- [ ] Kaggle token doğru hesapta, telefon doğrulaması yapılmış
- [ ] Kalan GPU kotası biliniyor ve buraya yazılmış
- [ ] Eşzamanlı koşu limiti ölçülmüş (varsayılmamış)
- [ ] `kx.py board` çalışıyor, `log/RUNS.md` boş ve hazır
- [ ] Yarışma açılır açılmaz katılım + kural kabulünü yapacak kişi belli
- [ ] Codex CLI cevap veriyor (bu oturumda 2 kez test edildi, çalışıyor)
