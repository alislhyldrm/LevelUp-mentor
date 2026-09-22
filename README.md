# LevelUp-mentor

> Digital mentor for SİPER

24 saatlik Kaggle yarışması için ajan sistemi. Bu depo bir model değil, bir
**çalışma düzeni**: deneylerin rastgele değil sırayla yapılmasını, sonuçların
karşılaştırılabilir olmasını ve kararların insanda kalmasını sağlıyor.

Sistem üç ajanla çalışır: **insan** karar verir ve koşturur, **Claude Code** kodu yazıp
doğrular ve kaydeder, **Codex** bağımsız ikinci uzman olarak beş sabit noktada devreye
girer.

> **Kaggle'a hiçbir şey otomatik gönderilmez.** Ne notebook, ne dataset, ne submission.
> Kaggle'dan yalnız yarışma verisi iner. Kaggle'a giden tek şey, insanın notebook
> editörüne kendi elleriyle yapıştırdığı koddur.

---

## Sistemin üç işi

1. **Teslim döngüsünü hızlandır.** Kod → koşu → çıktı → kayıt zinciri sürtünmesiz dönsün.
2. **Karşılaştırılabilirliği garanti et.** Sabit fold, sabit metrik, sabit çıktı
   sözleşmesi. Bu olmadan iki skorun yan yana yazılması anlamsızdır.
3. **Tek bir "şu an ne var, sırada ne var" ekranı tut.** `STATUS.md`.

Bu üçüne hizmet etmeyen dosya kurulmaz.

---

## Akış

```
/case → ✋Onay 1 (CV + metrik) → baseline (Codex ile birlikte) → koşu: insan → skor
      → OOF hata analizi + BACKLOG → ✋Onay 2 → /exp döngüsü → ensemble
      → /final kapısı → gönderim (insan)
```

| Faz | Ne olur | Kim |
|---|---|---|
| 1 · Case | Ham sayfalar kaydedilir, 10 dakikalık triyaj, ürün bölümü, CV şeması | insan yapıştırır, Claude işler, Codex bağımsız denetler |
| 2 · Baseline | Tek hücrelik kod yazılır, Kaggle'da koşar, ilk güvenilir skor alınır | Claude + Codex yazar, insan koşturur |
| 3 · Liste | OOF hata analizi + önem sıralı backlog | Claude + Codex |
| 4 · Döngü | Backlog sırasıyla 8–15 deney, her biri tek hipotez | üçü birlikte |
| 5 · Ensemble | OOF'lar indirilir, ağırlıklar bulunur | insan indirir, Claude hesaplar |
| 6 · Final | Sabit 6 maddelik teslim kapısı | Claude + Codex, kararı insan verir |

Paralel hat: **ürün köprüsü** — jüri yalnız skora bakmadığı için model sadece skora
göre kurulmaz.

### Bir deney turu

```
1  Claude  backlog'dan madde seç — hipotez, dayanak, süre yazılamıyorsa deney açılmaz
2  Claude  code.py doldur (yalnız hazirla() ve model_kur() değişir)
3  Codex   riskliyse kod incelemesi — GEÇERSİZ KILAR çıkarsa kod verilmez
4  Claude  kodu + parent farkını insana ver
5  İnsan   Kaggle notebook'una yapıştır → Run All → çıktıyı geri ver
6  Claude  kayit — fold parmak izi + submission formatı doğrulanır
7  Claude  cmp — parent ile fold fold karşılaştırma
8  İnsan   KABUL / HAVUZ / RED
```

**Tek koşu, tek onay:** bir koşunun sonucu kaydedilmeden sıradaki kod verilmez.

---

## Klasörler

| Klasör | Ne işe yarar | Kim yazar |
|---|---|---|
| `case/` | Yarışmanın ham sayfaları ve triyaj tablosu. Çelişkide ham metin hakemdir | Claude, insanın yapıştırdığı metinden |
| `core/` | **Ortak sözleşme:** fold üretimi, metrik, CV kararı. D-01'den sonra sabittir | Claude, Onay 1'de |
| `data/` | Yarışma verisi. Repoya commit edilmez, makinede durur | Kaggle'dan iner |
| `experiments/` | Her deney bir klasör: `code.py` · `diff.md` · `card.md` · `output/` | Claude |
| `ensemble/` | OOF ağırlıkları ve karışım kaydı. Son fazda dolar | Claude |
| `log/` | Karar, backlog, koşu, gönderim, mentor kayıtları | Claude, insanın kararlarıyla |
| `plan/` | Sistemin neden böyle kurulduğu. Referans dosya | insan, kuruluşta |
| `product/` | İkinci aşama: tek girdiyle tahmin üreten servis | insan + Claude |
| `tools/` | `kx.py` ve yardımcıları | insan, kuruluşta |

Her klasörde ne zaman dolduğunu anlatan bir `README.md` var.

---

## Araçlar

```bash
python tools/kx.py new EXP-007 --parent EXP-003 --note "<hipotez>"   # deney aç
python tools/kx.py kayit EXP-007                                     # çıktıyı doğrula ve kaydet
python tools/kx.py cmp EXP-007                                       # parent ile karşılaştır
python tools/kx.py board                                             # durum panosu

python tools/make_folds.py --target <hedef> [--pos <etiket>]         # D-01'den sonra bir kez
python tools/test_kx.py                                              # 21 doğrulama senaryosu
```

`kx.py` Kaggle CLI'yi **hiç çağırmaz.** Bir PreToolUse hook'u yanlışlıkla çalışacak
gönderim komutlarını ayrıca engeller.

---

## Fold parmak izi

Kaggle'a dataset yüklenmediği için fold garantisi dosya paylaşımı değil,
**aynı kodu çalıştırıp aynı parmak izini üretmek**tir.

`core/folds_snippet.py` her `code.py`'ye aynen gömülür. Koşu, fold dizisinin
12 haneli md5'ini ekrana basar:

```python
hashlib.md5(fold.tobytes()).hexdigest()[:12]
```

`kx.py kayit` bunu yereldeki `core/folds.csv`'nin izi ile karşılaştırır. **Tutmazsa
sonuç kayda girmez** — skor ne olursa olsun. Tek satır bile başka parçaya düşmüşse
iz değişir; bölmenin sessizce kayması böyle yakalanır.

---

## Karar kuralı

| Durum | Karar |
|---|---|
| Tüm fold'larda iyileşme **veya** ortalama fark fold sapmasından belirgin büyük | **KABUL** — yeni ana hat |
| Ortalama pozitif, tutarsız | **HAVUZ** — ensemble adayı, ana hat değişmez |
| Ortalama negatif | **RED** — OOF yine saklanır |
| Fark küçük | Daha basit/hızlı model korunur |

"BELİRSİZ" yok. Koşu hatası bir fikre RED yazdırmaz; "koşmadı" olarak kaydedilir.
**Kötü skor hata değildir** — hata, kodun koşmaması veya çıktı üretmemesidir.

---

## Sabitlenen kararlar

`log/DECISIONS.md` içinde tam hâli. Özet:

- **K-01** Kaggle'a hiçbir şey gönderilmez
- **K-02** Koşuyu insan yapar
- **K-03** Tek koşu, tek onay
- **K-04** Akışta zorunlu submission yok — gönderim kararı insanın
- **K-05** Tek ortak Kaggle hesabı
- **K-06** Fold garantisi parmak iziyle
- **K-07** Gece kuyruğu ve nöbet düzeni yok

---

## Durum

**Case bekleniyor.** Kurulum tamam, `python tools/test_kx.py` 21/21 geçiyor.
Güncel durum her zaman [`STATUS.md`](STATUS.md)'de; en üst satırı "insandan sıradaki
eylem"dir.

Nereye bakılacağı: kurallar [`CLAUDE.md`](CLAUDE.md), Codex protokolü
[`CODEX.md`](CODEX.md), sistemin gerekçesi [`plan/`](plan/).
