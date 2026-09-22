# Kaggle Hekaton — Proje Kuralları

## Rol
İnsan karar verir ve submit eder. Sen notebook yazarsın, `kx.py` ile koşturursun,
çıktıları doğrular, karşılaştırır ve kaydedersin. Sorulara dosyadan cevap verirsin.

## Nasıl kazanılır (bunu her deneyden önce oku)
- **Rastgele baseline + üstüne rastgele değişiklik yok.** Her deney `log/BACKLOG.md`'den
  gelir ve tek bir hipotez taşır. Ana hat oturmadan önceki keşif deneyleri istisnadır;
  `card.md`'de "keşif" işaretlenir ve karar kuralına girmez.
- Kod yazmadan önce dört satır: hangi backlog maddesi · hangi hipotez · hangi dayanak ·
  tahmini kaç dakika. Bu dördü yoksa deney açılmaz.
- **Genel öncelik sırası:** veri/CV düzeltmeleri > veri temsili ve feature >
  model ailesi > eğitim detayı > hiperparametre. Yukarıdaki kırıksa aşağısı boşa gider.
- **Hata analizi beş deney beklemez.** İlk güvenilir baseline'dan hemen sonra kısa bir
  OOF hata analizi yapılır. Amaç fikir listesi üretmek değil, bir sonraki deneyi
  değiştirecek **tek bulgu** aramaktır.
- Bu veride ölçülmüş bir gözlem ("hatanın %60'ı en uzun %10 örnekte"), dış kaynaklı
  genel bir fikirden daha güçlü dayanaktır.
- İki ajanın aynı fikri önermesi o fikrin başarı olasılığını artırmaz.

## Kurallar
1. Fold'lar ve metrik D-01'den sonra sabittir. Sadece kanıtlanmış bir kusur (sızıntı,
   gruplama ihlali) için değişir; değişirse yeni CV sürümü açılır ve mevcut en iyi aday
   bu sürümde yeniden ölçülür. Eski ve yeni skorlar aynı tabloda karşılaştırılmaz.
2. Çıktı sözleşmesine (`core/cv_spec.md`) uymayan sonuç kayda girmez.
3. Ana hat oturduktan sonra her deney tek hipotez taşır. Teknik olarak zorunlu birlikte
   değişiklikler aynı deneyde kalır.
4. Sonucu alınmış deney klasörü değiştirilmez, yeni deney açılır. "Hata" = notebook
   koşmadı veya çıktı üretmedi. **Kötü skor hata değildir.**
5. Hiçbir OOF/test tahmini silinmez. RED çıkanlar da ensemble havuzunda kalır.
6. CV'de beklenmedik büyük sıçramada önce sızıntı araştırılır.
7. **Submit etme.** Öner; insan gönderdikten sonra `log/SUBMISSIONS.md`'ye kaydet.
8. Her kayıttan sonra `STATUS.md`'yi güncelle (≤60 satır). En üst satır her zaman
   "insandan sıradaki eylem"dir. Gerçek takip yoksa "izliyorum" deme, son kontrol
   saatini yaz. Dosya append edilmez, her seferinde yeniden yazılır: her bölümün
   satır tavanı vardır, geçmiş üç katmanda zaman bazlı çürür ("Bu oturumda ne oldu"
   → "Önceki oturum" → "Öncesi", en eskisi tek satıra iner). Ana hat, sabitlenen
   kararlar ve "Denendi, işe yaramadı" çürümez — bunlar kaybolursa aynı fikir
   tekrar denenir.
9. Kayıtta olmayan şey için "kayıtta yok" de, uydurma. Ölçülmemiş skoru sayı olarak verme.
10. Codex'e her çağrı `CODEX.md`'deki sabit kapla yapılır. Serbest metin çağrı yok.

## Karar kuralı (`kx.py cmp` çıktısıyla)
| Durum | Karar |
|---|---|
| Tüm fold'larda iyileşme **veya** ortalama fark fold sapmasından belirgin büyük | **KABUL** — yeni ana hat |
| Ortalama pozitif, tutarsız | **HAVUZ** — ana hat değişmez, OOF ensemble adayı. Farklı seed ile tekrar koşulmaz |
| Ortalama negatif | **RED** — OOF yine saklanır |
| Fark küçük | Daha **basit/hızlı** model korunur |

"BELİRSİZ" yok. Koşu hatası veya eksik çıktı bir fikre RED yazdırmaz; "koşmadı" olarak kaydedilir.

## Soru → nereye bak
| Soru | Dosya |
|---|---|
| Şu an ne var, sırada ne var | `STATUS.md` |
| Kural, metrik, format, ürün notu | `case/CASE.md` |
| Veri tipine göre tuzaklar | `case/TRAPS.md` |
| Fold mantığı, ana skor, FAST tanımı | `core/cv_spec.md` |
| Fikrin kaynağı | `log/RESEARCH.md` |
| Neden bu deney | `log/BACKLOG.md` |
| Deney sonuçları | `experiments/EXP_SUMMARY.md` → `EXP-xxx/card.md` |
| Kaggle'da ne koşuyor | `log/RUNS.md` |
| İnsan kararları | `log/DECISIONS.md` |
| Mentor ne dedi, ne sormalıyız | `log/MENTOR.md` |
| Ne gönderildi | `log/SUBMISSIONS.md` |
| Codex'e nasıl çağrı yazılır | `CODEX.md` |

## Akış
`/case` → ✋Onay 1 (CV + metrik) → hızlı baseline + ilk submission → ✋Onay 2
→ backlog → `/exp` döngüsü → ensemble → `/final` kapısı → final seçimi (insan)

## Oturum başı / oturum sonu
Yarışma günü tek sohbette bitmez; birden çok oturum açılır. Bağlam **sadece
`STATUS.md` üzerinden** taşınır.
- **Başta:** ilk iş `STATUS.md`'yi okumak. Üç satırla özetle — "buradayız /
  nerede kalmıştık / insandan sıradaki eylem" — sonra dur, dosyayı değiştirme.
- **Sonda:** insan "compact", "clear", "yeni oturum", "ara veriyorum",
  "kapatıyorum" dediğinde `STATUS.md` kural 8'deki çürüme mantığıyla
  yeniden yazılır.

## Kurtarma kuralları
- Submission limiti dolduysa: OOF'ta biriktir, UTC gece yarısı (TR 03:00) sıfırlanınca gönder.
- CV iyi LB kötü (veya tersi) ise: yeni deney açma, önce fold/gruplama ve format kontrolü.
- Notebook süre limitine yaklaşıyorsa: her fold sonunda ara çıktı yazacak şekilde böl.
- Codex 10 dk içinde dönmezse: o adımı atla, insana bildir, sıradaki işe geç.
- Veri CLI ile inmiyorsa (403): insana "yarışma kurallarını siteden kabul et" de.
- Kişi azaldıysa: yeni FULL koşu açma, mevcut adayları tamamla ve ensemble'a git.

## Tekrarlanan hatalar
- **Kernel başlığı = slug olmalı.** Kaggle, başlık kendi slugify'ıyla `id`'ye tam
  dönüşmezse sessizce kendi ürettiği farklı bir slug kullanır; `status`/`fetch` o zaman
  yanıltıcı "izin reddedildi" hatasıyla patlar. `kx.py` başlığı zaten `= slug` yapıyor ve
  push sonrası otomatik doğruluyor — elle `kernel-metadata.json` düzenleme.
- **`/kaggle/input/` yolu sabit değil.** Notebook editöründe düz `/kaggle/input/<slug>/`,
  `kaggle kernels push` ile (CLI/batch) başlatılan koşularda ise iç içe
  `/kaggle/input/competitions/<slug>/` ve `/kaggle/input/datasets/<owner>/<slug>/` olabilir.
  Şablon artık `rglob` ile arıyor, sabit yol yazma.
- **`status` "RUNNING" derken koşu gerçekte bitmiş olabilir** (prova: ~19 dk gecikme
  görüldü). `runtime_min` sadece notebook-içi süreyi ölçer, Kaggle kuyruk+son-işleme
  süresini içermez. `status` COMPLETE demeden de `fetch` dene — sonuç gerçekten yoksa
  doğrulama zaten reddeder, zararı olmaz. FULL koşu zamanlamasında bu payı hesaba kat.
- **Kaggle'ın sklearn sürümü yerelden farklı olabilir** (provada 1.6.1 vs yerel 1.9.1).
  İndirilen `model.pkl` yerelde `pickle.load` ile açılamayabilir. Final kapısı madde 5
  ("model temiz oturumda yüklendi mi") bunu **aynı ortamda** (Kaggle notebook içinde veya
  eşleşen sklearn sürümüyle) test etsin, yerel farklı sürümle "açılmadı" diye YANLIŞ RED verme.
- **Deney açmadan önce gerçekten `log/BACKLOG.md`'ye yaz.** Provada bir TRAPS bulgusu
  backlog'a hiç girmeden doğrudan `kx.py new` ile denendi; `EXP-xxx` skill'in "dört satır
  yoksa açma" kuralı sözde kaldı. Backlog boşsa önce oraya yaz, sonra deneyi aç.
- **`kx.py fetch` `EXP_SUMMARY.md`'deki "Karar" sütununu doldurmaz** — bu insan/ajanın
  `cmp` sonrası elle güncellemesi gereken bir alan. `card.md` güncellenince
  `EXP_SUMMARY.md` satırını da aynı anda güncelle, unutma.
