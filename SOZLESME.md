# SÖZLEŞME — takım kodu için tek sayfa

Okur: kendi sisteminde kod yazan takım arkadaşı ve onun ajanı. Bu sayfadaki şartları
taşıyan koşunun sonucu ortak kayda, karşılaştırmaya ve ensemble'a girer.

## 1. Kimlik
- Her kişiye bir yüzlük: `kx.json` → `owners` (ör. `"3": "ay"` → `EXP-301…399`).
  Claude `0xx/1xx`, Codex `2xx`.
- Kaggle notebook adı `kx.py new` çıktısında yazar (ör. `ay-exp-301`). Tek ortak hesap:
  her deney kendi adıyla yeni notebook'ta koşar.

## 2. İskelet
- Kod `python tools/kx.py new EXP-3xx --parent EXP-0yy --note "<hipotez>"` ile üretilir
  (ya da koordinatörden alınan `code.py`). Fold ve metrik blokları `core/`'dan aynen gömülü.
- Değişen yerler yalnız: `TEKNIKLER`, `hazirla`, `fold_hazirla`, `model_kur`, `egit`,
  `tahmin`. Fold/metrik blokları, döngü ve çıktı bloğu olduğu gibi kalır.
- Koşu `FOLD PARMAK IZI` basar; `core/cv_spec.md`'deki izle aynı olan sonuç kayda girer.
- Her deney tek hipotez taşır ve dört satırla açılır: backlog maddesi · hipotez ·
  dayanak · tahmini dakika.

## 3. Koşu ve teslim
- Kodu insan inceler ve kendisi koşturur: Kaggle notebook'u (tek hücre, Run All) veya
  yerelde `python experiments/EXP-3xx/code.py`. Gönderim kararı insanındır; kod yalnız
  dosya üretir.
- Başlatmadan önce koordinatöre haber ver: ortak hesabın eşzamanlı koşu limiti paylaşılıyor.
- Teslim: ekran çıktısının tamamı (`=== KX RESULT JSON ===` bloğu dahil). Ensemble
  aşamasında ek olarak `oof.parquet` + `test_preds.parquet`.
- Kayıt, karşılaştırma ve karar önerisi koordinatörde (`kx.py kayit` → `cmp`).

## 4. Teknik kuralları
Kurallar bu sistemin kısıtından doğar: sabit fold'lar, OOF ile karar, 24 saat, ortak GPU.
Uygulanan her teknik `TEKNIKLER`'e tek satır girer: ne · neden · sızıntı nasıl önlendi.

**Sızıntı — fold içi fit.** Hedefe bakan veya istatistik öğrenen her dönüşüm (target
encoding, scaler, imputer, hedefe göre feature seçimi, oversampling) `fold_hazirla`'da
yalnız `Xtr, ytr` ile fit edilir; `Xva`/`Xte`'ye yalnız transform uygulanır. Target
encoding'in iç bölmesi de aynı grup/zaman sınırını korur. `hazirla` satır-içi dönüşümler
içindir (oran, tarih parçası, uzunluk, donmuş modelden embedding). Train+test ortak
istatistik (frekans) de orada durabilir; `card.md` "Ürün etkisi"ne not düşülür.

**CV.** Şema D-01'de sabitlenir (`core/cv_spec.md`, `FOLD_SCHEME`). Test ayrımının kanıtı
`python tools/adv_val.py`: AUC yüksekse şema test ayrımını taklit eder, kayan kolonlar
backlog'a girer.

**Metriğe özel son işlem.** Eşik (F1/MCC), QWK kesimleri, clipping OOF üzerinde aranır ve
teste aynı değer uygulanır; değer `card.md`'ye yazılır. Hedef dönüşümü metriği izler
(RMSLE → `log1p` ile eğit, `expm1` ile geri). Kaynak: `core/metrik-katalogu.md`.

**Early stopping.** İç ayrım (`Xtr` içinden) veya `Xva`: ilk baseline'da seçilir, bütün
deneylerde aynı kalır.

**HPO.** Ana hat oturduktan sonra, FAST modda en çok 30 dk; en iyi set tek FULL koşuyla
ölçülür. `card.md`: "parametre aynı fold'larda arandı, skor hafif iyimser".

**Pseudo-label.** Yalnız `egit` içinde, fold içi: fold modeli `Xte`'yi tahmin eder,
yüksek güvenli satırlar eklenir, model yeniden fit edilir; etiketler yalnız test
satırlarından gelir. Code competition'da (test gizli) ve test train'den küçükken BEKLE.

**Ensemble.** Değer farklı model ailesinden gelir (GBDT + NN/lineer). AUC/AP'de
`blend.py --rank`. Ağırlık aranan OOF skoru bağımsız doğrulama sayılmaz; stacking aynı
fold'larla kurulur. Seed averaging yalnız final için seçilen modelde.

**Bellek.** `KUCULT = True` büyük veride; karar baseline'da verilir, sonraki deneyler aynı
ayarla koşar ki fark modelden gelsin.

**Transfer öğrenme.** Önce ucuz yol: donmuş önceden eğitilmiş modelden embedding →
`hazirla`'da feature → GBDT (CPU). Fine-tune GPU kotası kontrol edildikten sonra, küçük
backbone ve az epoch ile. İnternet kapalıysa ağırlıkları insan notebook'a Kaggle Models /
dataset girdisi olarak ekler.
