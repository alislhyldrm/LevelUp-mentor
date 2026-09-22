# Codex protokolü

Codex "bazen fikrini soracağımız başka bir ajan" değildir. Sınırları, girdileri ve
çıktıları belli bir uzman eklentidir. **Beş çağrı tipi vardır, başka çağrı yoktur.**
Her çağrı aşağıdaki sabit kapla yapılır — böylece "Codex'e ne göndereceğim" diye
düşünmek gerekmez.

---

## Sabit çağrı kabı

    ## Codex çağrısı

    ### Görev
    <Validation denetimi / kod incelemesi / bağımsız deney / fikir üretimi / final kontrolü>

    ### Okunacak dosyalar
    - <tam yol>
    - <tam yol>

    ### Tek soru
    <Tek ve karar verilebilir soru>

    ### İstenen çıktı formatı
    <Alanları ve en fazla uzunluğu açıkça yaz>

    ### Yapma
    - Belirtilmeyen dosyaları değiştirme.
    - Eksik bilgiyi tahmin ederek gerçekmiş gibi sunma.
    - İstenen kapsam dışında yeni sistem veya araç önerme.
    - Merkezi kayıt dosyalarını değiştirme (STATUS.md, BACKLOG.md, EXP_SUMMARY.md, CASE.md).
    - Ölçülmemiş skor etkisini sayı olarak verme.

Codex'e önceki bağlamı bildiğini varsayma. Okunacak dosyaların **tam yolunu** her çağrıda yaz.

---

## Kimlik ayrımı (Kaggle hesabı paylaşıldığı için zorunlu)

| | Deney no | Kernel slug | Klasör |
|---|---|---|---|
| Claude | `EXP-0xx`, `EXP-1xx` | `as-cl-exp-017` | `experiments/EXP-017/` |
| Codex | `EXP-2xx` | `as-cx-exp-217` | `experiments/EXP-217/` |

- Codex **yalnız** `EXP-2xx` klasörlerine yazar.
- Her `card.md`'de `owner`, `kernel_slug`, Kaggle notebook versiyonu ve koşu durumu bulunur.
- Var olan bir slug'a push etmeden önce slug'ın deney kimliği doğrulanır (`kx.py push` yapar).
- Merkezi dosyaların (STATUS, BACKLOG, EXP_SUMMARY) **tek yazarı Claude'dur.** Codex
  sonucu yapılandırılmış döndürür, merkezi kayda Claude işler.

> Tek Kaggle hesabında yalnızca farklı yerel dosya kullanmak izolasyon sağlamaz.
> Aynı slug'a push, birinin koşusunun diğerinin üstüne yazılması demektir — sessiz ve
> geri alınamaz kayıp.

---

## Çağrı 1 — Metrik + **validation** denetimi

**Ne zaman:** Faz 0, veri iner inmez. **Süre:** 20 dakika, sert sınır.
**Nasıl:** EDA ile **paralel**, sıralı değil. Kritik yolda olduğu için bekletilmez.

Yanlış metrik fark edilir: skor tuhaf çıkar, yön ters görünür.
**Yanlış bölme fark edilmez:** CV yükselir, ilerlediğini sanırsın, LB'de çöpe çıkar —
ve tüm deney geçmişini geçersiz kılar. Codex'i pahalı olana bakmak için kullan.

### Kural

> Codex, Claude'un önerisini **görmeden** bağımsız validation önerisi hazırlar.
> İki öneri çakışırsa karar ajanların anlatım gücüne göre verilmez. Hakem;
> train/test grup örtüşmesi, zaman aralıkları, ID yapısı, tekrarlar, veri üretim süreci
> ve test ayrımına ilişkin gözlemlerdir. Her öneri, **test setinin nasıl oluşturulduğuna
> dair açık bir hipotez** yazmalı ve bu hipotezi veri bulgularıyla desteklemelidir.

### Çatışma çözülmezse

> Gerçek test yapısına aykırı **iyimserlik üretme riski düşük** olan şema ana validation
> olarak seçilir. Alternatif şema "duyarlılık kontrolü" olarak `core/cv_spec.md`'de saklanır.
> İki şemada model sıralaması değişiyorsa validation belirsizliği açıkça kaydedilir ve
> ilk submission'lar bu belirsizliği sınamak için kullanılır.

Zaman varsa iki basit baseline iki şemada da koşulur. Zaman yoksa leakage riski düşük olan
(daha sıkı) şema seçilir — **fakat bunun yalnızca pesimist skor üreteceği iddia edilmez.**
Gereğinden sıkı bölme: skoru fazla düşürebilir, model ailelerinin sıralamasını değiştirebilir,
fold'u küçültüp sonucu kararsızlaştırabilir, gerçek test dağılımından farklı bir problem ölçebilir.

### İstenen çıktı formatı

    - Öneri: <bölme şeması, tek paragraf>
    - Test-ayrım hipotezi: <test seti nasıl oluşturulmuş, tek cümle>
    - Veri kanıtı: <bu hipotezi destekleyen ölçülmüş gözlemler>
    - Leakage riski: <hangi yolla sızabilir>
    - Belirsizlik: <neyi göremedim>
    - Metrik: <resmi formülden yazılan implementasyon + uç durumlar + skor yönü>

Metrik standart bir metrikse sıfırdan yazmak yerine güvenilir bir kütüphane
implementasyonuyla karşılaştırmak yeterlidir. Uyuşma tek başına yetmez: resmi örnek,
elle hesaplanabilen küçük örnekler, skor yönü, sınıf sırası ve uç durumlar da kontrol edilir.
Metrikte hakem **resmi formüldür.** Uyuşmazlık 20 dakikada çözülmezse basit olan seçilir
ve `log/DECISIONS.md`'ye D-xx olarak kaydedilir.

---

## Çağrı 2 — Kod incelemesi (riskli deneylerde)

**Ne zaman:** Sadece veri işleme, feature veya hedef değişkene dokunan deneylerde,
**push'tan önce.** Yalnız parametre değişen deneylerde atlanır.

**Sayısal skor etkisi istenmez.** Codex koşmadan bilemez, uydurur. Üç kademe:

| Kademe | Anlam | Eylem |
|---|---|---|
| **GEÇERSİZ KILAR** | Leakage, yanlış fold, yanlış metrik, hedefin girdiye karışması, hatalı tahmin eşlemesi | Kaggle'a yükleme **durdurulur** |
| **RİSKLİ AMA ÖLÇÜLEBİLİR** | Sonucu etkileyebilecek ama deneyi geçersiz kılmayan sorun | Yükleme devam eder; risk `card.md`'ye yazılır |
| **KOZMETİK** | Okunabilirlik, isimlendirme, skoru etkilemeyen yapı | Engellenmez |

### İstenen çıktı formatı

    - Kademe: GEÇERSİZ KILAR | RİSKLİ AMA ÖLÇÜLEBİLİR | KOZMETİK
    - Konum: <dosya / hücre no>
    - Neden: <tek cümle>
    - En küçük düzeltme: <tek cümle>

Bulgu yoksa Codex açıkça **"yüklemeyi durduracak bulgu yok"** der.
Bu ifade kodun tamamen doğru olduğuna dair garanti sayılmaz.

Uzun genel değerlendirme isteme. Denetim 30 saniyede okunabilir olmalı; yoksa gece
yarısı kimse okumaz.

---

## Çağrı 3 — Bağımsız model hattı

Claude bir GBDT yazarken Codex farklı bir mimari yazar.

**Şart:** Codex'in notebook'u da fold ve metriği `hackathon-core`'dan okur ve çıktı
sözleşmesine (`core/cv_spec.md`) birebir uyar. Uymazsa ensemble'a alınmaz.

Not: Ensemble'a değer katan şey farklı **model hatalarıdır**, farklı yazarın farklı
**uygulama hataları** değil.

### İstenen çıktı formatı

    - EXP: EXP-2xx
    - Slug: as-cx-exp-2xx
    - Hipotez: <tek cümle>
    - Değişen parçalar: <ana hatta göre ne farklı>
    - Çıktılar: <sözleşmedeki dosyalar üretildi mi>
    - Çalıştırma gereksinimi: <GPU? internet? ek dataset?>

---

## Çağrı 4 — Fikir üretimi

**Ne zaman:** İlk backlog kurulurken ve `log/BACKLOG.md`'de 3'ten az ŞİMDİ maddesi kaldığında.

**Kısıt sorunun içine gömülür.** Boşlukta "skoru nasıl artırırız" sorulmaz — ders kitabı
cevabı üretir. Doğru soru biçimi:

> "Kalan üç saatte yapılabilecek **en değerli üç deney**, gerekçesi ve süresiyle."

Girdi: `case/CASE.md` + `log/RESEARCH.md` + son OOF hata analizi.

### İstenen çıktı formatı

    En fazla 3 fikir. Her biri:
    - Fikir: <tek cümle>
    - Dayanak: <bu veride ölçülmüş gözlem veya kaynak>
    - Uygulanacak değişiklik: <somut>
    - Tahmini süre: <dk, notebook döngüsü sürtünmesi dahil>

---

## Çağrı 5 — Final teslim kapısı

**Ne zaman:** Final aday seçiminden önce. **Sabit liste, serbest inceleme değil.**

23. saatte, uykusuzken en olası felaket "yanlış model fikri" değildir; yanlış sürümü
seçmek, satır sırasının kayması, ensemble ağırlıklarının farklı bir OOF setinden gelmesi,
modelin temiz oturumda yüklenmemesi. Bunlar sıfır yaratıcılık gerektiren, sabit listeyle
yakalanan hatalar — ikinci bir ajana devredilecek en uygun iş tam da budur.

### Kural

> Her madde `GEÇTİ / KALDI / DOĞRULANAMADI` olarak cevaplanır. `KALDI` veya
> `DOĞRULANAMADI` bulunan aday **final için önerilemez.** Kanıt olarak dosya yolu,
> EXP kimliği, koşu/versiyon bilgisi veya kontrol sonucu yazılır.

### Kontrol listesi

1. Seçilen dosya hangi `EXP`, mod, seed ve Kaggle koşu/versiyonundan geldi?
2. Submission satır sayısı ve ID sırası örnek submission ile birebir aynı mı?
3. Tahmin kolonları ve varsa sınıf sırası doğru mu?
4. Ensemble ağırlıkları hangi OOF setiyle hesaplandı; bu OOF'lar submission üreten
   **aynı model koşularına** mı ait?
5. Ürün için korunacak model temiz oturumda yüklenip örnek girdiden tahmin üretebildi mi?
6. Code competition ise inference notebook'u **internet kapalıyken** temiz oturumda
   uçtan uca tamamlandı mı?

> 4. madde özellikle önemli: aynı deney adı altında sonradan yeniden çalıştırılmış
> modellerin OOF'u ile farklı test tahminlerini karıştırmak sessiz ama ölümcül bir hatadır.
> Bu yüzden yalnız EXP numarası değil, **koşu kimliği / Kaggle versiyonu** da eşleşmeli.
