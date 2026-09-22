# Kaggle Hekaton — Proje Kuralları

## Rol
İnsan karar verir, koşturur ve gönderir. Sen kodu yazarsın, insana verirsin, dönen
çıktıyı doğrular, karşılaştırır ve kaydedersin. Sorulara dosyadan cevap verirsin.

**Kaggle'a hiçbir şey göndermezsin.** Ne notebook, ne dataset, ne submission.
Kaggle'dan yalnız yarışma verisi indirilir. Kaggle'a giden tek şey, insanın notebook
editörüne kendi elleriyle yapıştırdığı koddur. `tools/kx.py` Kaggle CLI'yi hiç çağırmaz.

## Baseline'dan hemen sonra: liste zorunlu
İlk baseline (`EXP-001` veya case'in ilk deneyi) skorunu aldıktan sonra, **başka hiçbir
deney açmadan önce** `log/BACKLOG.md` doldurulur ve insana gösterilir:
1. `CODEX.md` Çağrı 4'ü (fikir üretimi) çağır — girdi: `case/CASE.md` + `case/TRAPS.md`
   bulguları + baseline sonucu. Bağımsız bir fikir listesi iste.
2. Kendi bulgularını (TRAPS taraması, OOF hata analizi) da aynı listeye ekle.
3. `log/BACKLOG.md`'yi doldur (ŞİMDİ/SONRA/BEKLE, dayanak sütunu boş bırakılmaz).
4. **Listeyi insana göster** — dosyaya yazıp geçme, sohbette de ver.
Boş backlog'dan deney açılmaz; tek bir ad-hoc fikri sırayı atlayıp test etmek de bu
kuralı ihlal eder. Bu adım atlanırsa iterasyon rastgele baseline üstüne rastgele
değişiklik olur — planın en başta reddettiği şey tam olarak budur (bkz. "Nasıl kazanılır").

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
4. Sonucu alınmış deney klasörü değiştirilmez, yeni deney açılır. "Hata" = kod
   koşmadı veya çıktı üretmedi. **Kötü skor hata değildir.**
5. Hiçbir OOF/test tahmini silinmez. RED çıkanlar da ensemble havuzunda kalır.
   Her koşuda yalnız ekran çıktısı kaydedilir; OOF dosyaları **ensemble aşamasında**
   insan tarafından indirilir (`experiments/EXP-xxx/output/`). O ana kadar OOF sadece
   Kaggle koşusunun çıktısında durur — `blend.py` dosyalar inmeden çalışmaz.
6. CV'de beklenmedik büyük sıçramada önce sızıntı araştırılır.
7. **Gönderme.** Gönderim kararı insanındır ve saat hedefine bağlı değildir. Sen yalnız
   hazır aday önerirsin: EXP no · ana skor · dosya yolu · format kontrolü sonucu.
   İnsan gönderdikten sonra `log/SUBMISSIONS.md`'ye kaydet.
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
| Hangi koşu yapıldı | `log/RUNS.md` |
| Koşulacak kod | `experiments/EXP-xxx/code.py` (+ `diff.md`) |
| İnsan kararları | `log/DECISIONS.md` |
| Mentor ne dedi, ne sormalıyız | `log/MENTOR.md` |
| Ne gönderildi | `log/SUBMISSIONS.md` |
| Codex'e nasıl çağrı yazılır | `CODEX.md` |

## Akış
`/case` → ✋Onay 1 (CV + metrik) → baseline (Codex ile birlikte yazılır) → **koşu: insan**
→ skor → OOF hata analizi + `log/BACKLOG.md` → ✋Onay 2 → `/exp` döngüsü → ensemble
→ `/final` kapısı → final seçimi ve gönderim (insan)

Akışta **zorunlu submission yoktur.** Gönderim kararı insanındır, saat hedefine bağlı
değildir; sen yalnız gönderilmeye hazır aday önerirsin.

**✋Onay 2 tek tanım:** baseline skoru + OOF hata analizi + dolu `log/BACKLOG.md` aynı
pakette insana sunulur. Onay gelmeden iterasyon başlamaz.

### Tek koşu, tek onay
Bir koşunun sonucu kaydedilmeden sıradaki kod verilmez. Art arda birkaç koşu planlayıp
insanı sonuçta bilgilendirmek bu kuralın ihlalidir. Her turda:
kodu ver (+ parent farkı) → insan koşturur → çıktıyı ver → `kayit` → `cmp` → karar.

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
- **`/kaggle/input/` yolu sabit değil.** Notebook editöründe düz `/kaggle/input/<slug>/`
  olur ama iç içe dizinler de görülür. `code_template.py` `rglob` ile arıyor — sabit yol yazma.
- **Fold parmak izi tutmuyorsa sonuç kayda girmez.** Kaggle'a dataset yüklenmediği için
  fold garantisi dosya paylaşımı değil, `core/folds_snippet.py`'nin aynen gömülmesi +
  parmak izi eşitliğidir. `code.py` içindeki fold bloğu elle düzenlenirse bütün geçmiş
  karşılaştırmalar geçersiz olur.
- **Kaggle'ın sklearn sürümü yerelden farklı olabilir** (provada 1.6.1 vs yerel 1.9.1).
  Yerelde açılmayan bir `model.pkl` için "açılmadı" diye YANLIŞ RED verme; final kapısı
  madde 5 bunu **aynı ortamda** test eder.
- **Deney açmadan önce gerçekten `log/BACKLOG.md`'ye yaz.** Provada bir TRAPS bulgusu
  backlog'a hiç girmeden doğrudan denendi. Backlog boşsa önce oraya yaz, sonra deneyi aç.
- **`kx.py kayit` `EXP_SUMMARY.md`'deki "Karar" sütununu doldurmaz** — bu `cmp` sonrası
  elle güncellenir. `card.md` güncellenince `EXP_SUMMARY.md` satırını da aynı anda güncelle.
- **Atlanan doğrulamayı sessizce geçme.** Dosyalar inmediyse `kayit` hangi kontrolleri
  atladığını yazar; bunlar `card.md`'deki "Atlanan doğrulama" satırına geçer.
