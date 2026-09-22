# Kaggle Hekaton Sistemi — Final Plan (v4)

> **Bu dosya kodlama ajanı içindir.** Plan modunda oku, uygulama planı çıkar, onay almadan dosya oluşturma.
> Bu dosyada olmayan araç, hook, mod, agent veya skill ekleme. Bir şey eksik görünüyorsa tahmin etme, sor.
> **Değerlendirme kriteri:** Bir parça, yarış sırasında insana iş çıkarıyorsa değil, iş azaltıyorsa kurulur.
>
> **v4.1 — akış değişti.** Kaggle'a hiçbir şey gönderilmez (ne notebook, ne dataset, ne gönderim).
> Koşuyu insan yapar: ajanın verdiği tek hücrelik kod Kaggle notebook'una yapıştırılır.
> Bu dosya ile `CLAUDE.md` çelişirse **`CLAUDE.md` kazanır.**

---

## 0. Sabit bağlam

- Kaggle aşaması: **Cuma 12:00 → Cumartesi 12:00** (24 saat). Sonrasında aynı işten ürün çıkarılacak ikinci aşama var.
- **Kod Kaggle notebook'unda koşar.** Lokalde sadece: notebook üretimi, çıktı analizi, karşılaştırma, ensemble ağırlığı.
- **Takımın tek bir Kaggle hesabı var.** 6 kişi bu hesabı paylaşıyor → GPU kotası ve eşzamanlı koşu limiti **ortak kaynaktır**. Bu, planın en sert kısıtı.
- Takım 6 kişi ve **herkes kendi ajan sistemini kuruyor.** Bu repo, çıktıların birleştiği yer. Dolayısıyla bu sistemin birinci işi "en iyi modeli bulmak" değil, **6 farklı yerden gelen sonucun karşılaştırılabilir ve birleştirilebilir olmasını garanti etmek.**
- Veri tipi önceden bilinmiyor.
- **Submission'ı insan yapar.** Ajan submit etmez; hangi dosyanın neden gönderilebileceğini söyler ve gönderileni kaydeder.

---

## 1. Sistemin üç işi — bundan fazlası yok

1. **Teslim döngüsünü otomatikleştir.** Notebook → Kaggle → çıktı → kayıt zinciri elle dosya taşımadan dönsün.
2. **Karşılaştırılabilirliği garanti et.** Sabit fold, sabit metrik, sabit çıktı sözleşmesi. Bu olmadan 6 kişinin sonucu birleşmez.
3. **Tek bir "şu an ne var, sırada ne var" ekranı tut.** `STATUS.md`. Aynı zamanda
   oturumlar arası devir dosyasıdır — tek sohbette bitmeyen yarış günü boyunca
   bağlam yalnız bu dosya üzerinden taşınır.

Bu üç işe hizmet etmeyen her dosya kurulmaz.

---

## 2. Bilerek yapılmayacaklar (bunları tekrar önerme)

| Yapılmayacak | Neden |
|---|---|
| 6 faz skill'i | 2 skill yeter: `/case`, `/exp`. Gerisi CLAUDE.md'de tek paragraf. |
| 4 hazır domain playbook'u | Model bu bilgiyi zaten biliyor. Yerine tek bir ~40 satırlık "tuzaklar" kontrol listesi. |
| Özel subagent tanım dosyaları (`researcher`, `data-analyst`) | Paralel araştırma, skill içindeki prompt şablonuyla doğrudan görev olarak açılır. Ayrı dosya bakım yükü. |
| `SUB-04 ← EXP-017 ← B-05 ← R-02` tam ID zinciri | Muhasebe yükü. Sadece `parent` + tek satır gerekçe tutulur. |
| Backlog puan formülü (`Kazanç×Olasılık/Süre` veya türevleri) | Uydurma sayılara sahte kesinlik. Yerine 3 kova: ŞİMDİ / SONRA / BEKLE. |
| A=0.6 / B=0.4 gibi sabit olasılık katsayıları | Aynı sebep. |
| 5 adımlı çapraz beyin fırtınası protokolü | Token ve dakika yakar. Yerine 10 dakikalık tek tur, sadece 2 anda. |
| Otomatik "tier" geçişi (2 başarısızlıkta ince ayara geç) | Başarısızlığın sebebi hipotez mi uygulama mı, bunu kural değil insan ayırt eder. |
| 4 ayrı başlangıç notebook şablonu | Tek şablon + veri tipine göre doldurulan bölüm. |
| Otomatik submit | Kural riski ve geri alınamazlık. |

---

## 3. Klasör yapısı

```
hackathon/
├── CLAUDE.md
├── AGENTS.md            # tek satır: "Kurallar CLAUDE.md'dedir, onu oku." (Codex bunu okur)
├── STATUS.md            # tek ekran: savaş planı + şu an + sıradaki 3 iş + riskler
├── RUNS.md              # paylaşılan Kaggle hesabının koşu kuyruğu (aşağıda)
├── DECISIONS.md         # D-xx: insan kararları, tek satır
├── case/
│   ├── CASE.md
│   ├── TRAPS.md         # veri tipine göre tuzak kontrol listesi (~40 satır, tek dosya)
│   └── pages/           # yarışma sayfalarının metni
├── core/                # fold sözleşmesi — YEREL, Kaggle'a yüklenmez
│   ├── folds.csv
│   ├── metric.py
│   └── cv_spec.md
├── research/RESEARCH.md
├── backlog/BACKLOG.md
├── experiments/
│   ├── EXP_SUMMARY.md
│   └── EXP-xxx/{notebook.ipynb, card.md, kernel-metadata.json, output/}
├── ensemble/
├── submissions/SUBMISSIONS.md
├── product/             # ikinci aşama köprüsü (Bölüm 10)
├── tools/{kx.py, blend.py}
└── .claude/skills/{case, exp}/SKILL.md
```

---

## 4. Ortak sözleşme — planın en kritik bölümü

6 kişi 6 farklı sistemde çalışacak. Aşağıdakilere uymayan çıktı **karşılaştırmaya ve ensemble'a alınmaz.** Bu sözleşme Cuma öğleden sonra takımın tamamına tek sayfa olarak dağıtılır.

### 4.1 `core/` — fold sözleşmesi (YEREL, Kaggle'a yüklenmez)
Onay 1'den sonra `core/` yerelde kurulur:
- `folds_snippet.py` → fold üretim kodu + parmak izi fonksiyonu. **Tek doğruluk kaynağı.**
- `folds.csv` → `tools/make_folds.py` üretir: `id, fold, y`. Yerelde kalır.
- `metric.py` → tek fonksiyon: `score(y_true, y_pred) -> float` + `GREATER_IS_BETTER` sabiti.
- `cv_spec.md` → fold mantığı, gruplama anahtarı, **ana skorun hangisi olduğu** (bkz. 4.3), **fold parmak izi**.

Kaggle'a dataset yüklenmediği için garanti dosya paylaşımı değil **kod eşitliğidir**:
`folds_snippet.py` ve `metric.py`'nin metni `kx.py new` tarafından `code.py`'ye aynen
gömülür, koşu fold parmak izini ekrana basar, `kx.py kayit` bunu yerel `folds.csv` ile
karşılaştırır. Tutmayan sonuç kayda girmez.

### 4.2 Çıktı sözleşmesi
Her koşu `/kaggle/working/` altına şunları yazar:

| Dosya | İçerik |
|---|---|
| `oof.parquet` | **`id` kolonu + tahmin kolon(lar)ı.** Kimliksiz `.npy` yasak. Çok sınıflıysa kolon adları sınıf adlarıdır. |
| `test_preds.parquet` | Aynı format, test kimlikleriyle. |
| `submission.csv` | Yarışmanın istediği tam format. |
| `result.json` | `{exp_id, parent, mode, seed, fold_scores[], cv_mean, cv_oof, n_folds_done, n_rows_oof, runtime_min, git_note}` |

`kx.py kayit` bu dosyaları **otomatik doğrular** (fold parmak izi dahil): id kolonu var mı, satır sayısı folds.csv ile eşleşiyor mu, NaN/tekrar var mı, `n_folds_done` tam mı. Biri tutmazsa sonuç kayda girmez, ekrana hata basar. Bu kontrol, gece yarısı fark edilen hizalama hatasının tek panzehiri.

### 4.3 İki skor birden
`cv_mean` (fold skorlarının ortalaması) ve `cv_oof` (birleştirilmiş OOF üzerinden tek hesap) **ikisi de** yazılır. AUC, F1, MAP gibi metriklerde bunlar farklıdır. `cv_spec.md` hangisinin ana skor olduğunu Onay 1'de sabitler; karar ve sıralama hep onunla yapılır.

### 4.4 Adlandırma (tek hesap paylaşıldığı için zorunlu)
Kernel slug'ı: `<isim-baş-harfleri>-exp-<no>` → `as-exp-017`. Deney klasörü: `EXP-017`. Çakışma olmaz.

---

## 5. Otomasyon: `tools/kx.py`

Tek dosya. **Kaggle CLI'yi hiç çağırmaz** — ne kernel, ne dataset, ne gönderim.
Yerelde üretir, doğrular, karşılaştırır; koşuyu insan Kaggle notebook'unda yapar.

```
kx.py new   EXP-017 --parent EXP-012 --note "target encoding"
            → klasör + code.py (tek hücre, fold+metrik gömülü) + card.md + diff.md
kx.py kayit EXP-017
            → output/run_log.txt'deki KX RESULT JSON bloğundan result.json üretir,
              Bölüm 4.2 doğrulaması + fold parmak izi kontrolü, EXP_SUMMARY.md + RUNS.md
kx.py cmp   EXP-017
            → parent ile fold fold karşılaştırma tablosu + karar için kanıt (Bölüm 8.3)
kx.py board
            → tek ekran: sonuçlar, bekleyenler, en iyi aday, yerel fold parmak izi
```

Koşu döngüsü: kodu insana ver (+ `diff.md`) → insan Kaggle'da `Run All` → ekran çıktısı
`output/run_log.txt`'ye → `kx.py kayit`. **Tek koşu, tek onay:** önceki koşu kaydedilmeden
sıradaki kod verilmez.

**Gönderim otomatikleştirilmez.** `kx.py` sadece "şu dosya şu sebeple gönderilebilir"
satırını basar; insan gönderir, `SUBMISSIONS.md`'ye tek satır düşülür.

`tools/blend.py`: ~60 satır. OOF'lar üzerinde önce **eşit ağırlıklı** karışımı ölçer, sonra sınırlı sayıda (≤200 adım) ağırlık denemesi yapar. Aşırı uyum riskine karşı kural: **ağırlık araması yapılan OOF skoru bağımsız doğrulama sayılmaz**; ensemble ancak en iyi tek modeli fold bazında da geçiyorsa kabul edilir.

### 5.1 `RUNS.md` — paylaşılan hesabın kuyruğu
Tek hesap, 6 kişi. Push etmeden önce `kx.py board` bakılır. Satır formatı:

```
| slug | kim | başlangıç | GPU? | tahmini bitiş | durum |
```

Kurallar:
- GPU gerektirmeyen her şey **CPU'da koşar** (tablo/GBDT dahil). GPU kotası derin öğrenmeye ve uzun FULL koşulara saklanır.
- Eşzamanlı koşu limiti hesap başınadır ve GPU tarafında dardır. **Gerçek limiti Cuma 11:00 provasında ölç**, CASE.md'ye yaz, varsayma.
- Kalan GPU kotası Cuma 11:00'de ve gece 00:00'da kontrol edilir, STATUS.md'ye yazılır.

---

## 6. `CLAUDE.md` (kurulacak tam metin)

```markdown
# Kaggle Hekaton — Proje Kuralları

## Rol
İnsan karar verir ve submit eder. Sen notebook yazarsın, kx.py ile koşturursun,
çıktıları doğrular, karşılaştırır ve kaydedersin. Sorulara dosyadan cevap verirsin.

## Kurallar
1. Fold'lar ve metrik D-01'den sonra sabittir. Sadece kanıtlanmış bir kusur (sızıntı,
   gruplama ihlali) için değişir; değişirse yeni CV sürümü açılır ve mevcut en iyi aday
   bu sürümde yeniden ölçülür. Eski ve yeni skorlar aynı tabloda karşılaştırılmaz.
2. Çıktı sözleşmesine (CASE.md Bölüm "Sözleşme") uymayan sonuç kayda girmez.
3. Ana hat oturmadan önce keşif deneyleri birden fazla değişiklik içerebilir; card.md'de
   "keşif" olarak işaretlenir ve karar kuralına girmez. Ana hat oturduktan sonra her deney
   **tek hipotez** taşır (teknik olarak zorunlu birlikte değişiklikler aynı deneyde kalır).
4. Sonucu alınmış deney klasörü değiştirilmez, yeni deney açılır. "Hata" = notebook koşmadı
   veya çıktı üretmedi. Kötü skor hata değildir.
5. Hiçbir OOF/test tahmini silinmez. RED çıkanlar da ensemble havuzunda kalır.
6. CV'de beklenmedik büyük sıçramada önce sızıntı araştırılır.
7. Submit etme. Öner, insan gönderdikten sonra SUBMISSIONS.md'ye kaydet.
8. Her kayıttan sonra STATUS.md'yi güncelle (≤30 satır). STATUS.md'nin en üstü her zaman
   "insandan sıradaki eylem" satırıdır. Gerçek takip yoksa "izliyorum" deme,
   son kontrol saatini yaz.
9. Kayıtta olmayan şey için "kayıtta yok" de, uydurma.

## Soru → nereye bak
STATUS.md (durum) · case/CASE.md (kural, metrik, format) · research/RESEARCH.md (fikrin kaynağı)
· backlog/BACKLOG.md (neden bu deney) · experiments/EXP_SUMMARY.md → EXP-xxx/card.md (sonuç)
· submissions/SUBMISSIONS.md · DECISIONS.md · RUNS.md (Kaggle'da ne koşuyor)

## Akış
/case → ✋Onay 1 (CV + metrik) → baseline (Codex ile) → koşu: insan → skor
→ OOF hata analizi + backlog → ✋Onay 2 (kontrol listesi) → /exp döngüsü → ensemble
→ final seçimi ve gönderim (insan)

## Kurtarma kuralları
- Submission limiti dolduysa: OOF'ta biriktir, UTC gece yarısı (TR 03:00) sıfırlanınca gönder.
- CV iyi LB kötü (veya tersi) ise: yeni deney açma, önce fold/gruplama ve format kontrolü.
- Notebook süre limitine yaklaşıyorsa: her fold sonunda ara çıktı yazacak şekilde böl.
- Codex 10 dk içinde dönmezse: o adımı atla, insana bildir, sıradaki işe geç.
- Veri CLI ile inmiyorsa (403): insana "yarışma kurallarını siteden kabul et" de.
- Kişi azaldıysa: yeni FULL koşu açma, mevcut adayları tamamla ve ensemble'a git.
- Koşu hatası / eksik çıktı, model fikrine RED yazdırmaz; sadece "koşmadı" olarak kaydedilir.

## Tekrarlanan hatalar
- (boş — insan "kural ekle" dediğinde buraya eklenir)
```

---

## 7. Yarış akışı — saat saat

| Saat (T+) | İş | Kayarsa ne kesilir |
|---|---|---|
| **11:00 (T−1)** | Hazırlık kontrol listesi (Bölüm 12.3) | — |
| 12:00 (T+0:00) | **İlk 10 dakika triyaj:** code competition mı? metrik ve yönü? submission formatı? günlük limit? internet/süre kısıtı? → CASE.md'nin ilk 10 satırı | — |
| 12:10 | Veri `kaggle competitions download` ile iner. Paralel: fast-track notebook iskeleti | — |
| 12:45 | **Fast-track koşu (insan yapıştırır, Run All).** Sabit/medyan tahmin veya ham GBDT. Amaç skor değil, zincirin çalıştığını tescil etmek | — |
| 13:30 | **Format kontrolünden geçmiş, gönderilmeye hazır ilk `submission.csv` hedefi.** Sert sınır: 15:00. Gönderme kararı insanın | Basitleştir, daha basit tahminle üret |
| 12:45–14:00 | Paralel: EDA, train/test farkı, gruplama anahtarı, metrik yazımı (+ Codex bağımsız kontrolü) | EDA kısalır, fold mantığı korunur |
| 14:00 | **✋ Onay 1:** CV şeması + metrik + ana skor (`cv_mean` mi `cv_oof` mu) sabitlenir → D-01. `core/` yerelde kurulur, `make_folds.py` koşar, parmak izi `cv_spec.md`'ye yazılır | — |
| 14:00–14:45 | **Araştırma: 45 dakikalık sert kutu.** 3 paralel arama görevi. Çıktı kapsamlı özet değil: "şimdi denenecek 3 fikir, dayanağı, maliyeti". Paralel: güçlü baseline yazılır | 30 dakikaya in, baseline'a geç |
| 14:45–16:15 | **Tek güçlü baseline** FULL koşu. İkinci model ailesi ancak ilk sonuç ve kota görüldükten sonra açılır | İkinci aile iptal |
| 16:15 | **✋ Onay 2 kontrol listesi** (Bölüm 8.4) | — |
| 16:30–17:00 | Backlog: en fazla 10 madde, ilk 3'ü koşulabilir ayrıntıda | 6 madde, ilk 2'si ayrıntılı |
| 17:00–08:00 | **Deney döngüsü.** Gerçekçi hedef: 8–15 deney (yükleme/indirme sürtünmesi dahil). Uzun bir FULL koşudan önce aynı kodun kısa bir denemesi başarıyla bitmiş olmalı | FULL yerine FAST; düşük öncelikli maddeler iptal edilir |
| **02:30** | Cuma'nın kalan gönderim hakları 03:00'te yanar. İnsan karar verir; ajan hazır adayları teslim kartıyla sunar | — |
| 08:00–09:00 | Son deneyler. **Son FULL başlatma saati = 12:00 − (ölçülen koşu süresi × 1.5) − 45 dk.** Bu saat STATUS.md'ye yazılır ve geçilmez | — |
| 09:00–10:30 | Ensemble + (code competition ise) **tek inference notebook'unun uçtan uca çalışması** | Eşit ağırlıklı 2–3 model karışımıyla yetin |
| 10:30–11:15 | Final aday submission'ları (insan) | — |
| 11:15–11:30 | Final seçimi | — |
| 11:30–12:00 | Tampon. **Yeni deney yok; sadece mevcut adayı kurtaran düzeltme yapılır** | — |

Paralel iş kolu: **Cuma akşamından itibaren en az 1 kişi ürün iskeletine başlar** (Bölüm 10). Kaggle döngüsünü beklemez.

---

## 8. Deney protokolü

### 8.1 Notebook kuralları
- `code.py` başlığı: EXP ID, parent, hipotez, mod (FAST/FULL), seed, GPU gereksinimi, tahmini süre **aralığı** (tek sayı değil).
- Veri yolları **açıkça doğrulanır**: beklenen dosya adı ve şema kontrol edilir, birden fazla eşleşmede sessizce devam edilmez.
- Fold bloğu `core/folds_snippet.py`'den, metrik `core/metric.py`'den **aynen gömülür**; kod kendi fold'unu üretmez. Koşu fold parmak izini basar.
- Fit edilen her dönüşüm fold içinde fit edilir.
- Her fold bitince skor basılır ve **ara çıktı diske yazılır** (süre limitine takılırsa yarısı kurtulur).
- Çıktılar Bölüm 4.2 sözleşmesine uyar.
- **Ürün için:** eğitilmiş ağırlıklar + ön işleme nesneleri `/kaggle/working/artifacts/` altına kaydedilir (bkz. Bölüm 10).

### 8.2 FAST modu sabit reçetedir
`FAST = True` tek başına yetmez. FAST'ın **tek bir sabit tanımı** olur: aynı eğitim alt kümesi, aynı validation satırları, aynı iterasyon bütçesi. Bu tanım `cv_spec.md`'ye yazılır. FAST sonuçları yalnızca FAST ile karşılaştırılır, "tam CV" diye sunulmaz. FAST'ta zayıf çıkan fikir kesin elenmiş sayılmaz; daha uzun eğitim isteyen fikirler için not düşülür.

### 8.3 Karar kuralı (otomatik değil, kanıtla)
`kx.py cmp` şunları basar: ana skor farkı, fold fold farklar, fold farklarının standart sapması, varsa önemli alt grupların davranışı, ek koşu maliyeti. Öneri kuralı:

- Tüm fold'larda iyileşme **veya** ortalama fark fold farklarının standart sapmasından belirgin olarak büyük → **KABUL**, yeni ana hat.
- Ortalama pozitif ama tutarsız → **HAVUZ**: ana hat değişmez, OOF saklanır, ensemble adayı olur. **Farklı seed ile tekrar koşulmaz** (yeni bilgiye göre 30–40 dk çok pahalı).
- Ortalama negatif → **RED**, OOF yine saklanır.
- Fark küçükse **daha basit / daha hızlı model korunur.**

"BELİRSİZ" durumu kaldırıldı; yerine ana hattı bloklamayan HAVUZ geldi.

### 8.4 ✋ Onay 2 kontrol listesi
- [ ] Koşunun fold parmak izi yerel `core/folds.csv` ile aynı mı?
- [ ] Fit edilen her şey fold içinde mi?
- [ ] `oof.parquet` / `test_preds.parquet` **id kolonlu** mu, satır sayısı tam mı?
- [ ] `submission.csv` format kontrolünden geçti mi (kolon, satır, id sırası, NaN)?
- [ ] OOF hata analizi yapıldı mı, `log/BACKLOG.md` dolu ve insana gösterildi mi?
- [ ] Bir FAST deney kaç dakika, bir FULL deney kaç dakika sürüyor? (STATUS.md'ye yazıldı mı?)
- [ ] Kalan GPU kotası ve eşzamanlı koşu limiti biliniyor mu?

### 8.5 `card.md` (kısa tutulur)
```markdown
# EXP-017  (parent: EXP-012 | keşif? hayır)
- Hipotez: <tek cümle>
- Değişiklik: <parent'a göre tam olarak ne>
- Mod/Seed/GPU: FULL / 42 / hayır
- Sonuç: ana skor 0.8421 (parent 0.8398) | fold: +,+,+,−,+ | sapma 0.0031
- Karar: KABUL / HAVUZ / RED
- Ders: <tek cümle>
- Ürüne izi: <sadece KABUL ise tek cümle; değilse boş>
```

---

## 9. Backlog — formülsüz

`backlog/BACKLOG.md`, üç kovalı tek tablo:

```markdown
| Kova | B | Fikir | Dayanak | Tahmini dk | Not |
|---|---|---|---|---|---|
| ŞİMDİ | B-03 | Fold içi target encoding | R-02 (kazanan çözüm) | 35 | ilk 3'ten biri, ayrıntılı |
| SONRA | B-07 | İkinci model ailesi (NN) | ensemble çeşitliliği | 60 | kota uygunsa |
| BEKLE | B-11 | Dış veri ekleme | spekülatif | 45 | kural teyidi lazım |
```

- **En fazla 10 madde.** Sadece ŞİMDİ kovasındaki 3 madde koşulabilir ayrıntıdadır. Liste veri geldikçe gelişir; baştan eksiksiz liste çıkarmaya çalışılmaz.
- **"Kim önerdi" ile "hangi kanıta dayanıyor" ayrıdır.** `CODEX` / `İNSAN` öneren kişidir, kanıt değildir. Buna karşılık *"hatanın %60'ı en uzun %10 örnekte"* gibi bu veride ölçülmüş bir gözlem, dış kaynağı olmasa da en güçlü dayanaktır — ve genelde dış kaynaklı fikirlerden daha değerlidir.
- İki ajanın aynı fikri önermesi başarı olasılığını artırmaz.
- Tahmini süreye **notebook döngüsü sürtünmesi dahildir**; hiçbir madde 20 dakikanın altında yazılmaz.
- Genel eğilim: veri/CV düzeltmeleri > veri temsili ve feature > model ailesi > eğitim detayı > hiperparametre.
- Her 3–5 deneyde bir kova dağılımı gözden geçirilir; sebebi tek satır yazılır.
- **Hata analizi beş deney beklemez.** İlk güvenilir baseline'dan hemen sonra kısa bir OOF hata analizi yapılır; amaç fikir listesi üretmek değil, **bir sonraki deneyi değiştirecek tek bulgu** aramaktır.

---

## 10. Ürün köprüsü — ikinci aşama

Değerlendirmelerin üçünün de ortak tespiti: plan buraya hiç bakmıyordu. Minimum ama zorunlu set:

1. **CASE.md'ye 15 dakikalık ürün bölümü** (Faz 0'da, Onay 1'i beklemeden): kullanıcı kim, tahmin hangi kararı destekliyor, gerçek kullanımda hangi girdiler olacak, model nerede başarısız oluyor.
2. **Artefakt kuralı:** KABUL alan her deney `output/artifacts/` altına şunları bırakır: eğitilmiş ağırlık/model dosyası, ön işleme nesneleri ve tokenizer, sınıf/feature sırası, paket sürümleri.
3. **`product/predict.py`:** tek bir JSON/satır girdisi alıp tahmin döndüren tek giriş noktası. Tamamlanma ölçütü "model kaydedildi" değil, **"temiz bir oturumda yüklenip tekrar tahmin üretti"**.
4. **Ürün adayı ile yarışma adayı aynı olmak zorunda değil.** Yarışmada 8 modelli ensemble seçilebilir; ürün için hızlı tek model korunur. Bu ikisi Faz 5'te ayrı ayrı işaretlenir.
5. **Dikkat:** Sadece yarışma dosyasının toplu istatistiklerinden türeyen feature'lar (global mean/target encoding vb.) yeni bir kullanıcı girdisinde nasıl üretilecek? KABUL anında tek satır not düşülür.
6. **Paralel iş kolu:** Cuma akşamından itibaren en az 1 kişi arayüz/servis iskeletini sahte bir modelle kurar. Kaggle'ın bitmesini beklemez; Cumartesi öğlen yapılacak tek iş `predict.py`'yi bağlamaktır.
7. **STATUS.md'nin son satırı her zaman:** "Ürüne taşınabilecek en güçlü 3 bulgu: …"

---

## 11. Code competition ihtimali — ayrı bir dal

Faz 0'ın ilk 10 dakikasında netleşir. Eğer notebook submission ise:

- Test verisi koşu anında değişir → `test_preds.parquet` gerçek testi içermez. **Ensemble, seçilen modellerin ağırlıklarını OOF üzerinde bulur; sonra TEK bir inference notebook'u tüm modelleri yükleyip karıştırır.**
- Bu inference notebook'u **en geç Cumartesi 09:00'da ilk kez uçtan uca çalışmış olmalıdır.** Eğitim notebook'unun çalışması yeterli sayılmaz.
- İnternet kapalıysa paketler ve ağırlıklar önceden Kaggle dataset'i / Kaggle modeli olarak hazırlanır. Bu, eğitim koşularının çıktılarının dataset'e dönüştürülmesi demektir; ilk kez Cumartesi sabahı denenmez.
- Inference süre limiti kontrol edilir: kaç model sığar, hesapla ve STATUS.md'ye yaz.

---

## 12. Codex'in üç işi

Değerlendirmeler burada ayrışıyordu; karar: **fikir tartışması turları kaldırıldı, denetim ve bağımsız üretim kaldı.**

1. **Metrik doğrulaması (Faz 0, ~15 dk).** Codex, kodu görmeden Evaluation sayfasından metriği yazar. İki implementasyon rastgele girdilerde karşılaştırılır. **Ama uyuşma tek başına yeterli değil:** resmi örnek varsa onun sonucu, elle hesaplanabilen küçük örnekler, skor yönü, sınıf sırası ve uç durumlar da kontrol edilir. Standart bir metrikse sıfırdan yeniden yazmak yerine güvenilir bir kütüphane implementasyonuyla karşılaştırmak yeterlidir. **Uyuşmazlık 20 dakikada çözülmezse** resmi formül hakemdir; çözülmezse basit olan seçilir ve D-xx olarak kaydedilir.
2. **Yükleme öncesi sızıntı incelemesi (riskli deneylerde).** Sadece veri işleme, feature veya hedef değişkene dokunan deneylerde. Sorular: fold dışında fit var mı, gerçekten tek hipotez mi, fold/metrik core'dan mı okunuyor. Parametre değişikliklerinde atlanır.
3. **Bağımsız model hattı.** Claude bir GBDT yazarken Codex farklı bir mimari yazar. **Şart:** Codex'in kodu da `tools/code_template.py` iskeletini kullanır, fold ve metrik bloklarını `core/`'dan aynen gömer, aynı fold parmak izini basar ve Bölüm 4.2 sözleşmesine birebir uyar; uymazsa ensemble'a alınmaz. (Not: ensemble'a değer katan şey farklı **model hatalarıdır**, farklı yazarın farklı **uygulama hataları** değil.)

Ek: **10 dakikalık tek tur fikir alışverişi**, sadece iki anda — ilk backlog kurulurken ve backlog'da 3'ten az ŞİMDİ maddesi kaldığında. Girdi olarak CASE.md + RESEARCH.md + son OOF hata analizi verilir. Boşlukta "skoru nasıl artırırız" sorulmaz.

**Ortak dosyaların tek yazarı vardır:** STATUS, BACKLOG, EXP_SUMMARY'yi yalnızca koordinatör oturum günceller. Codex kendi deney klasöründe çalışır ve sonucu döndürür.

---

## 13. Cuma öncesi (4–6 saat)

### 13.1 Kurulum sırası
Her adım bitince kısa özet ver ve itiraz var mı diye sor.

| # | Ne | Süre |
|---|---|---|
| P0-1 | Kaggle CLI kurulumu + token testi (`kaggle competitions list`) | 15 dk |
| P0-2 | Klasör yapısı + boş şablonlar + `CLAUDE.md` + `AGENTS.md` | 30 dk |
| P0-3 | `tools/kx.py` (new/push/status/fetch/cmp/board) + çıktı doğrulaması | 75 dk |
| P0-4 | Tek notebook şablonu (Bölüm 8.1 kurallarına uyan) | 30 dk |
| P1-1 | `/case` ve `/exp` skill'leri (her biri ≤80 satır) | 30 dk |
| P1-2 | **Prova (Bölüm 13.2)** | 60–90 dk |
| P1-3 | Provada çıkan hataların düzeltilmesi | 30–45 dk |
| P2-1 | `tools/blend.py` + küçük testi | 30 dk |
| P2-2 | `case/TRAPS.md` (tablo/görüntü/metin/zaman serisi tuzakları, ~40 satır) | 20 dk |
| P2-3 | Sözleşmenin (Bölüm 4) takıma dağıtılacak tek sayfalık hali | 15 dk |

### 13.2 Prova — atlanmaz
Burada üç değerlendirmeden biriyle ayrılıyorum: prova kesilecek ilk şey değil, **en değerli hazırlık parçasıdır** — çünkü artık teslim döngüsü otomatik ve otomasyonun ilk kez yarışma sırasında denenmesi en pahalı hatadır. Ama 3–4 saatlik tam tur da gereksiz.

Kapanmış bir Playground yarışmasında **60–90 dakika**, sadece döngü:
1. `core/` dataset'ini Kaggle'a yükle, notebook'tan oku.
2. `kx.py new → push → status → fetch` tam olarak çalışıyor mu?
3. Çıktı doğrulaması bilerek bozuk bir dosyayı **yakalıyor mu?** (id kolonunu sil, test et.)
4. `kx.py cmp` iki deneyi fold fold karşılaştırıyor mu?
5. `blend.py` iki OOF'u birleştiriyor mu?
6. Ajana 3 soru sor ("son deneyde ne değişti?", "şu an en iyi aday ne?", "sırada ne var?") — doğru dosyaya bakıyor mu?

Ölçülen süreleri Bölüm 7 tablosuna işle. Çıkan hataları `CLAUDE.md` → "Tekrarlanan hatalar"a yaz. **Bu 6 madde çalışmıyorsa yeni bir şey yazmayı bırak, bunu düzelt.**

### 13.3 Cuma 11:00 kontrol listesi
- [ ] Kaggle token çalışıyor, telefon doğrulaması **yapılmış** (GPU ve internet için gerekli — Cuma sabahına bırakma)
- [ ] Kalan GPU kotası biliniyor ve STATUS.md'ye yazılmış
- [ ] Eşzamanlı koşu limiti ölçülmüş
- [ ] `kx.py board` çalışıyor, `RUNS.md` boş ve hazır
- [ ] Sözleşme tek sayfası 6 kişiye dağıtılmış
- [ ] Yarışma açılır açılmaz katılım ve kural kabulü yapılacak kişi belli

---

## 14. STATUS.md şablonu

`STATUS.md` aynı zamanda oturumlar arası devir dosyasıdır: append edilmez, her
güncellemede yeniden yazılır. Geçmiş üç katmanda zaman bazlı çürür — "Bu
oturumda ne oldu" (≤8 satır) → "Önceki oturum" (≤5 satır) → "Öncesi" (≤5 satır,
oturum başına tek satır, taşınca en eskiler birleşir). Ana hat, sabitlenen
kararlar ve "Denendi, işe yaramadı" çürümez — kaybolursa aynı fikir tekrar
denenir. Toplam ≤60 satır. Detay zaten kendi log dosyasındaysa buraya
kopyalanmaz, tek satır + dosya adı yazılır.

```markdown
# STATUS — <yarışma> | Cuma 12:00 → Cumartesi 12:00
<!-- Oturum devir dosyası. Yeni oturum önce bunu okur. Append edilmez, yeniden yazılır. -->

## İnsandan sıradaki eylem
→ <tek satır. Örn: "EXP-008 bitti, çıktı indi; EXP-009'u push etmemi onayla.">

## Şu an
Faz: … | Ana hat: EXP-… (ana skor …) | Son güncelleme: <gün HH:MM>
Kaggle'da koşan: … (tahmini bitiş …) | Kalan GPU kotası: … | Son FULL başlatma saati: …
Submission: kalan hak … (yenilenme TR 03:00) | En iyi LB: …

## Sıradaki 3 iş
1. …  2. …  3. …

## Bu oturumda ne oldu
- …

## Önceki oturum
- …

## Öncesi
- …

## Sabitlenen kararlar
- … (detay: log/DECISIONS.md)

## Denendi, işe yaramadı
- … (detay: experiments/EXP_SUMMARY.md)

## Aktif riskler
- …

## Nerede kaldım / dikkat
- …

## Ürüne taşınabilecek en güçlü 3 bulgu
1. …  2. …  3. …
```

---

## 15. Kurulumu bitirme ölçütü

Sistem, şu cümle doğru olduğunda hazırdır:

> "Ajana 'B-03'ü dene' dediğimde; notebook'u hazırlıyor, Kaggle'da koşturuyor, çıktıyı indirip
> doğruluyor, parent'la fold fold karşılaştırıyor, kaydediyor ve bana tek satırlık bir karar
> önerisi ile sıradaki işi söylüyor — ben arada hiçbir dosya taşımıyorum."

Bu cümle doğru değilse eksik olan parça tamamlanır. Doğruysa **yeni parça eklenmez.**
