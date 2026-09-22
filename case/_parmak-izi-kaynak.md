# Parmak izi taraması

Veriyi üreten süreç veride iz bırakır: ölçüm cihazının çözünürlüğü, sentetik üreticinin ızgarası, etiketleyicinin alışkanlığı, dışa aktarma aracının yuvarlaması. Bu izler genellenebilir ve izinli ise aday sinyaldir; kazanç ancak doğrulamayla görülür: iz değerin kendisinde değil, değerin **biçiminde** durur, ham çözüm onu temsil edemez.

**Bütçe:** tarama onaylı veri-inceleme dakikalarında biter. Örneklemi grup/zaman/nadir sınıf yapısına göre seç; kapsamasını kaydet. Bulgu tam doğrulamada sınanır.

**Çıktı:** tarama, kuyruğa yazılmış aday üretir ya da "bu iz sınıfı bu veride yok" satırı yazar. Süre dolan sınıf "incelenmedi" kalır; kanıt yokluğunu "iz yok" diye yazma.

## İzden adaya: kuyruk satırının biçimi

Her bulgu bu dört alanla `docs/DENEYLER.md` fikir kuyruğuna girer:

| alan | ne yazılır |
|---|---|
| gözlem | ölçülen sayı: "`Annual_Income` değerlerinin %6'sı tam 30000" |
| neden | izi bırakan süreç: "üretici tabandan kırpmış" |
| dönüşüm | öznitelik hali: "`x == 30000` göstergesi" |
| beklenen etki | büyüklük tahmini ve dakika maliyeti |

Nedeni yazılamayan gözlem kuyruğa girmez; dönüşümü yazılamayan gözlem de girmez.

## Deterministik bölge taraması (sayısal ya da sıralanabilir öznitelikte)

Hedefe bağlı bölge araması bir aday üretme yöntemidir; getirisi veriyle sınanır. Hedefin **tamamen belirlendiği** bölgeleri ara: bir aralıkta ya da kategoride hedef oranı 0 ya da 1'e çakılıyorsa, o bölge bir hipotezdir; bağımsız doğrulama olmadan genel kural sayılmaz.

```python
# egitim fold'unun ICINDE ara; dogrulamayi ayri fold'da yap
d = tr_fold[[col, target]].dropna().sort_values(col)
r = d[target].rolling(2000, center=True, min_periods=2000).mean()
# r'nin 0'a ya da 1'e yapistigi col araliklarini yaz
```

Kategorik sütunda `groupby(col)[target].agg(['mean', 'size'])`.

**Keşif sınırları** — aşağıdaki sayılar önceki prova sezgisidir, bilimsel eşik değildir. Veri büyüklüğü ve bağımsız grup sayısına göre gerekçelendir; doğrulamaya bakarak eşik seçme:

- **Asgari destek:** bir bölge en az 500 satır ya da toplamın %0,1'i kadar satır taşır. Altındaki bölgeler düşük destekli adaydır; otomatik olarak gürültü sayılmaz.
- **Keşif ve teyit ayrı:** sınırı eğitim fold'unda bul, validasyon fold'unda doğrula. Kararı metrik-uzmani verir; çelişki varsa tekrar ölç veya ele.
- **Aday tavanı:** sütun başına en çok 2 bölge kuyruğa girer. Çok sayıda sütunu tarayıp en iyi birkaçını seçmek, seçim yanlılığını ölçüye taşır.

## Tablo verisi

| İz | Ölçüm | Bulgu eşiği | Aday |
|---|---|---|---|
| Izgara | Sıralı benzersiz değerlerin ardışık farkı; mod ve OBEB | Farkların %90'ı tek bir adımın katı | Adıma bölüm ve kalan; adım sayısı |
| Kırpma | `min` ve `max` değerin frekansı | Beklenen yoğunluğun 5 katı | `x == min` göstergesi; kırpılmış nüfus ayrı ele alınır |
| Mod sıçraması | `value_counts().head(20)` komşu değerlerle karşılaştırılır | Komşuların 3 katı | O değere gösterge |
| Basamak | `(x // 10**k) % 10`, k = -4…4; basamak başına dağılım | Düzgünden sapma (ki-kare ya da gözle belirgin) | **Her basamak ayrı öznitelik.** Ölçüldü: 13 sütunun basamakları OOF'u +0,00176 taşıdı (5/5 fold) |
| Ondalık hane | Metin halinde nokta sonrası uzunluk | Birden çok hane sayısı | Hane sayısı özniteliği; farklı kaynak işareti |
| Kardinalite | `nunique() / len()` | >0,9 kimlik benzeri; <0,01 gizli kategorik | Gizli kategorikte frekans ve hedef kodlaması |
| Eksiklik deseni | Eksik maskesinin sütunlar arası ve hedefle ilişkisi | Hedefle ilişki rastgeleden ayrılıyor | Maskenin kendisi öznitelik |
| Sütun bağımlılığı | Bir sütun diğerlerinden tam hesaplanıyor mu | Tam eşleşme | Türetilmiş sütunu kaldır, bileşenleri tut |
| Satır sırası | `id` ya da satır indeksi ile hedefin ilişkisi | Rastgeleden ayrılan ilişki | Sıralama sızıntısı — validasyonu `metrik-uzmani` ayrım sözleşmesi ile düzelt |
| Kopya | Hedef dışı sütunlarda `duplicated()` | Aynı girdi farklı hedef | Gürültü tavanı; grup sızıntısı işareti |

Sayısalı **kategorik gibi** de ele al: değeri metne çevirip frekans ve hedef kodlaması uygula. Izgaraya oturmuş bir sayısalda bu, sürekli temsilin kaçırdığı tam-değer etkisini yakalar. Ölçüldü: basamakların üstüne frekans +0,00050, üçlü yumuşatmalı hedef kodlaması +0,00146 getirdi (aynı veri, 5/5 fold).

### Hedef kodlaması sızıntı sözleşmesi

Hedefi kullanan her kodlama — hedef ortalaması, WOE, sayım-ile-hedef, dış kaynaktan hedef istatistiği — **fold'un eğitim kısmında fit edilir**, validasyon ve test kısmına yalnız uygulanır. Tüm train üzerinde bir kez fit edilen kodlama OOF'u şişirir ve leaderboard'da çöker.

İç içe kaçak da kapatılır: kodlamayı dış fold içinde ikinci bir ayrımla üret. İç ayrım da grup/zaman sınırını korumalıdır; varsayılan rastgele `TargetEncoder(cv=...)` her senaryo için yeterli değildir.

Tamam: kodlayıcı fold döngüsünün **içinde** kuruluyor; aynı nesne farklı fold'lara taşınmıyor.

## Metin

| İz | Ölçüm | Aday |
|---|---|---|
| Şablon | En sık 5-gram'ların kapsadığı satır oranı | Şablon kimliği kategorik; şablon dışı kalan metin ayrı |
| Uzunluk kesilmesi | Uzunluk histogramında tek bir değerde yığılma (512, 1000) | `uzunluk == sınır` göstergesi |
| Kaynak kalıntısı | HTML etiketi, URL, kaçış dizisi, çift boşluk, bozuk kodlama içeren satır oranı | Her kalıntı türü için gösterge; kaynak kümesi kategorik |
| Alfabe | Karakter kümesi ve dil dağılımı | Dil/alfabe kategorik |
| Kopya | Tam ve yakın kopya (hash, MinHash) | Aynı metin farklı etiket → gürültü tavanı; train-test kopyası → sızıntı |

## Görüntü

| İz | Ölçüm | Aday |
|---|---|---|
| Boyut | Çözünürlük ve en-boy oranı kümeleri | Küme kimliği kategorik |
| Sıkıştırma | Dosya boyutu, JPEG kalite tahmini | Boyut ve kalite sayısal öznitelik |
| EXIF | Cihaz, tarih, yazılım alanlarının sınıflara göre dağılımı | Alan var/yok göstergesi; cihaz kategorik |
| Dosya adı | Addaki sayı ya da sıra ile hedefin ilişkisi | Sıralama sızıntısı uyarısı |
| Çerçeve | Kenar dolgusu, siyah bant, filigran oranı | Dolgu genişliği sayısal |
| Kopya | Algısal hash | Train-test kopyası → sızıntı |

## Zaman serisi

| İz | Ölçüm | Aday |
|---|---|---|
| Örnekleme | Damgalar arası farkın dağılımı | Beklenen aralıktan sapma göstergesi |
| Doldurulmuş boşluk | Arka arkaya tekrarlanan aynı değerin uzunluğu | Tekrar uzunluğu özniteliği |
| Yuvarlama | Değerlerin ızgara adımı; adımın tarihe göre değişimi | Rejim kimliği kategorik |
| Takvim | Hafta sonu, tatil, saat dilimi ve yaz saati kayması | Takvim öznitelikleri |
| Ölü seri | Bir tarihten sonra sabit ya da sıfır kalan birim | Ölü birim göstergesi; ayrı ele alınır |
| Aralık | Train ve test zaman aralıkları | Test geleceğe bakıyorsa validasyon da bakar (`metrik-uzmani` ayrım sözleşmesi) |

## Ses

| İz | Ölçüm | Aday |
|---|---|---|
| Format | Örnekleme hızı, kanal sayısı, bit derinliği kümeleri | Küme kimliği kategorik |
| Süre | Süre histogramı; tek değerde yığılma | `süre == sınır` göstergesi |
| Sessizlik | Baş ve sondaki eşik altı örnek sayısı | Dolgu uzunluğu sayısal |
| Kırpılma | Tam ölçek değerine değen örnek oranı | Kırpılma oranı sayısal |
| Kodek | Spektrumda üst kesim frekansı | Kesim frekansı → kaynak kodek kategorik |

## Dış kaynak bulunduysa

Künyenin 2. sorusu açık bir ata ya da kardeş veri bulduysa, kullanmadan önce beşi de cevaplanır:

1. **İzin:** yarışma kuralı dış veriye ne diyor (Rules, "External Data")? Lisans ticari/akademik kullanıma uygun mu?
2. **Erişilebilirlik:** kaynak bütün katılımcılara açık ve ücretsiz mi?
3. **Eşleştirme anahtarı:** hangi sütunlarla birleşiyor? Anahtar benzersiz mi, çoklu eşleşme var mı?
4. **Sızıntı:** dış kaynak yarışmanın test satırlarını ya da hedefini içeriyor mu? İçeriyorsa yerel skor anlamsızlaşır.
5. **Sürüm:** hangi sürüm, ne zaman indirildi? Kayıt `docs/DENEYLER.md`'ye yazılır.

Dış kaynaktan üretilen hedef istatistiği de yukarıdaki **sızıntı sözleşmesine** tabidir.

## Yorum sınırı

Tablodaki sayısal eşikler sezgisel tarama ayarlarıdır; birincil bilimsel dayanak olarak kullanılamaz. Önceki tek yarışmanın skorları tarihsel örnektir; yeni case kazanç vaadi değildir. `gap/BULGU.md` mevcut ortamda bulunmuyorsa eski sayıları bağımsız doğrulanmış kanıt diye aktarma. Tam veriye bakarak hedefe bağlı seçim yapmak validasyona sızıntı taşır.
