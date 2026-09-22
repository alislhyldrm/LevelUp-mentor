# TRAPS — veri tipine göre tuzak listesi

Veri iner inmez, EDA ile birlikte. **Önce "Her veri tipinde" bölümü** — oradaki altı
madde 24 saatin tamamını çöpe atabilen hatalardır. Sonra veri tipine uyan tabloya bak.

Bulgular `log/BACKLOG.md`'ye dört alanla girer:
**gözlem** (ölçülen sayı) · **neden** (izi bırakan süreç) · **dönüşüm** (öznitelik hali) ·
**beklenen etki + dakika**. Nedeni veya dönüşümü yazılamayan gözlem kuyruğa girmez.

---

## Her veri tipinde — sırayla, atlanmaz

| # | Tuzak | Ölçüm | Neden ölümcül |
|---|---|---|---|
| 1 | **Hedef kodlaması sızıntısı** | Hedefi kullanan her kodlama fold'un eğitim kısmında mı fit ediliyor? | Tüm train'de bir kez fit → OOF şişer, LB çöker. İç içe kaçak: iç ayrım da grup/zaman sınırını korumalı; varsayılan `TargetEncoder(cv=...)` her senaryoda yetmez |
| 2 | **Satır sırası sızıntısı** | `id` veya satır indeksi ile hedefin ilişkisi | Rastgeleden ayrılıyorsa CV anlamsız; ayrım şemasını düzelt |
| 3 | **Grup sızıntısı** | Hedef dışı sütunlarda `duplicated()`; aynı girdi farklı hedef | Aynı varlık iki tarafta → CV uydurma. Aynı zamanda gürültü tavanını gösterir |
| 4 | **Train-test kopyası** | Hash / algısal hash / MinHash ile çakışma | Varsa yerel skor anlamsızlaşır |
| 5 | **Sütun bağımlılığı** | Bir sütun diğerlerinden tam hesaplanıyor mu | Türetilmiş sütunu kaldır, bileşenleri tut |
| 6 | **Eksiklik deseni** | Eksik maskesinin hedefle ilişkisi | İlişki rastgeleden ayrılıyorsa maskenin kendisi özniteliktir |

---

## Tablo

| İz | Ölçüm | Eşik | Aday |
|---|---|---|---|
| Izgara | Sıralı benzersiz değerlerin ardışık farkı; mod ve OBEB | Farkların %90'ı tek adımın katı | Adıma bölüm ve kalan |
| Kırpma | `min`/`max` frekansı | Beklenen yoğunluğun 5 katı | `x == min` göstergesi; kırpılmış nüfus ayrı |
| Mod sıçraması | `value_counts().head(20)` komşularla | Komşuların 3 katı | O değere gösterge |
| Basamak | `(x // 10**k) % 10`, k=-4…4 | Düzgünden belirgin sapma | Her basamak ayrı öznitelik |
| Ondalık hane | Metinde nokta sonrası uzunluk | Birden çok hane sayısı | Hane sayısı = farklı kaynak işareti |
| Kardinalite | `nunique()/len()` | >0.9 kimlik benzeri; <0.01 gizli kategorik | Gizli kategorikte frekans/hedef kodlaması |

Sayısalı **kategorik gibi** de dene: değeri metne çevirip frekans kodlaması uygula.
Izgaraya oturmuş sayısalda bu, sürekli temsilin kaçırdığı tam-değer etkisini yakalar.

## Metin

| İz | Ölçüm | Aday |
|---|---|---|
| Şablon | En sık 5-gram'ların kapsadığı satır oranı | Şablon kimliği kategorik |
| Uzunluk kesilmesi | Uzunluk histogramında tek değerde yığılma (512, 1000) | `uzunluk == sınır` göstergesi |
| Kaynak kalıntısı | HTML etiketi, URL, kaçış dizisi, bozuk kodlama oranı | Tür başına gösterge |
| Alfabe | Karakter kümesi ve dil dağılımı | Dil/alfabe kategorik |

## Görüntü

| İz | Ölçüm | Aday |
|---|---|---|
| Boyut | Çözünürlük ve en-boy oranı kümeleri | Küme kimliği kategorik |
| Sıkıştırma | Dosya boyutu, JPEG kalite tahmini | Sayısal öznitelik |
| EXIF | Cihaz, tarih, yazılım alanlarının sınıflara göre dağılımı | Var/yok göstergesi; cihaz kategorik |
| Dosya adı | Addaki sayı/sıra ile hedefin ilişkisi | **Sıralama sızıntısı uyarısı** |
| Çerçeve | Kenar dolgusu, siyah bant, filigran oranı | Dolgu genişliği sayısal |

## Zaman serisi

| İz | Ölçüm | Aday |
|---|---|---|
| Aralık | Train ve test zaman aralıkları | **Test geleceğe bakıyorsa validasyon da bakar** |
| Örnekleme | Damgalar arası farkın dağılımı | Beklenen aralıktan sapma göstergesi |
| Doldurulmuş boşluk | Arka arkaya tekrarlanan aynı değerin uzunluğu | Tekrar uzunluğu özniteliği |
| Rejim | Izgara adımının tarihe göre değişimi | Rejim kimliği kategorik |
| Takvim | Hafta sonu, tatil, saat dilimi, yaz saati kayması | Takvim öznitelikleri |
| Ölü seri | Bir tarihten sonra sabit/sıfır kalan birim | Ölü birim göstergesi, ayrı ele alınır |

---

## Dış veri bulunduysa — beşi de cevaplanmadan kullanma

1. **İzin:** Rules → "External Data" ne diyor? Lisans uygun mu?
2. **Erişilebilirlik:** kaynak bütün katılımcılara açık ve ücretsiz mi?
3. **Eşleştirme anahtarı:** hangi sütunlarla birleşiyor, çoklu eşleşme var mı?
4. **Sızıntı:** yarışmanın test satırlarını veya hedefini içeriyor mu?
5. **Sürüm:** hangi sürüm, ne zaman indirildi? `log/RESEARCH.md`'ye yaz.

Dış kaynaktan üretilen hedef istatistiği de 1. maddedeki sızıntı sözleşmesine tabidir.

---

## Yorum sınırı

Buradaki sayısal eşikler **tarama ayarlarıdır**, bilimsel dayanak değil. Bir iz ancak
doğrulamada kazanç gösterirse aday olur. Tam veriye bakarak hedefe bağlı seçim yapmak
validasyona sızıntı taşır: sınırı eğitim fold'unda bul, validasyon fold'unda doğrula.
Sütun başına en çok 2 bölge kuyruğa girer — çok sütun tarayıp en iyisini seçmek
seçim yanlılığını ölçüye taşır.
