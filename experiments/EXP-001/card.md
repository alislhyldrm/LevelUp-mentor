# EXP-001 — D-FINE-S baseline, sıfırdan eğitim

| alan | değer |
|---|---|
| owner | Claude |
| parent | — (ilk baseline) |
| backlog maddesi | — (ilk baseline, keşif değil) |
| keşif mi | hayır |
| koşu yeri | Google Colab, **A100-SXM4-80GB (85,1 GB, 12 vCPU)** (Kaggle'a gönderim yok — K-01) |
| kod | `experiments/EXP-001/code.py` |
| repo | Peterande/D-FINE @ `956d1709314c2c6a4df6f34de232054578a7449f` (sabitlendi) |
| durum | **BİTTİ** — 60/60 epoch, 268 dk. Ana skor **AP50 = 0,59512** |

## Dört satır
- **Hangi backlog maddesi:** — (ilk baseline)
- **Hipotez:** 960 girişte sıfırdan eğitilmiş D-FINE-S, bu veride ölçülebilir bir mAP@0.5 zemini verir.
- **Dayanak:** EDA — kutuların %38'i <32², 640'a küçültünce p5 kutu kenarı ≈ 7 px (`case/CASE.md` satır 6).
- **Süre:** ÖLÇÜLDÜ (A100, tam epoch) → 4,5 dk/epoch × 60 epoch = **4,5 saat**.

## TEKNİKLER (ne · neden · sızıntı nasıl önlendi)
- **D-FINE-S / HGNetv2-B0, sıfırdan (rastgele başlatma)** · neden: D-03 dış veri yasağı +
  D-05 (Objects365 ağırlığı yasak, insan kararı) · sızıntı: yok, hiçbir dış ağırlık yüklenmiyor.
- **Giriş 960×960, yapılandırılmış config override ile** (regex değil) · neden: küçük nesne · sızıntı: yok.
- **Multiscale KAPALI** (`collate_fn.base_size_repeat: null`) · neden: 960 tabanda ölçek üretimi
  960'ın belirgin üstüne çıkar, T4 15,6 GB'ta OOM riski; baseline tek değişkenli kalsın · sızıntı: yok.
- **Augmentasyon repo varsayılanı** (PhotometricDistort + ZoomOut + IoUCrop + HFlip), son 7 epoch kapalı ·
  neden: baseline sade kalsın · sızıntı: yok.
- **LR sqrt ölçekleme:** repo S tarifi batch 64 / lr 4e-4 → batch 32'de lr 2,828e-4, backbone 1,414e-4 ·
  **ÖLÇÜLMEDİ**, bu veride sınanmadı.
- **Batch 32** (A100 80 GB'ta 64+ sığardı) · neden: epoch süresi batch'e değil görüntü sayısına bağlı;
  batch küçük tutmak epoch'u yavaşlatmadan optimizer adımını 80'den 161'e çıkarır. 5175 görüntülük
  sıfırdan eğitimde adım sayısı değerli · sızıntı: yok.
- **Warmup adım sayısına bağlı** (2 × adım/epoch = 322 iter) · neden: warmup İTERASYON cinsinden
  (`det_engine.py:119`) ve `lr_scheduler` warmup bitene kadar hiç adımlamıyor (`det_solver.py:94`).
  Sabit 1000 yazılsaydı batch 32'de 6,2 epoch, batch 48'de 9,3 epoch warmup olurdu · sızıntı: yok.
- **AMP (fp16)** · neden: T4 bellek/hız · sızıntı: yok.
- **Val = D-01 sabit bölmesi** (%20 stratified, seed 42) · sızıntı: train/val görüntü kesişimi
  koşuda zorunlu kontrol ediliyor, ölçüldü = 0.
- **Ana skor: geçici yerel AP50** — COCO, `maxDets=300`, 4 sınıf eşit ağırlıklı ortalama.

## Neden `maxDets=300`
Taslaktaki gerekçe ("COCO'nun 100'ü görüntü başı 218 kutuda keser") **yanlıştı**: COCO'nun 100 sınırı
görüntü **× sınıf** başına uygulanır. Doğru gerekçe ölçüldü: val'de **7 görüntü–sınıf çifti** 100 kutuyu
aşıyor (en yüksek 132); train'de 36 çift aşıyor (en yüksek 199). Sınır konursa bu çiftlerde GT kırpılır.

## Bölme parmak izi (K-06'nın tespit karşılığı)
Dataset yüklenmediği için garanti dosya paylaşımı değil, içerik özeti eşitliğidir. Koşuda zorunlu assert:

| bölme | görüntü | kutu | sha16 (dosya adları) | sınıf dağılımı (car/van/truck/bus) |
|---|---|---|---|---|
| train | 5175 | 132.989 | `3214f3fa7f9abfe8` | 100.485 / 18.265 / 9.632 / 4.607 |
| val | 1294 | 32.343 | `209e9c83a27b935c` | 24.342 / 4.521 / 2.477 / 1.003 |

Kategori sırası `[(0,car),(1,van),(2,truck),(3,bus)]` doğrulandı. train∩val = **0 görüntü**.

## SMOKE koşusu (boru hattı testi, skor karşılaştırmasına GİRMEZ)
256 train / 128 val görüntü, 2 epoch. `RUN_DIR=.../EXP-001_smoke`.
- DOĞRULA satırı geçti: `num_classes 4` · `epochs 2` · `eval_spatial_size [960,960]` ·
  `base_size 960` · `base_size_repeat None` · train/val `Resize [960,960]` · `HGNetv2.pretrained False`.
- Model 10,18 M parametre, 52,46 GFLOPS (ileri, 960).
- AP50 epoch 0 = 0,0000 · epoch 1 = 0,0010 (2 epoch rastgele başlangıçtan; beklenen).
- KX RESULT bloğu bu koşuda üretilmedi — hücre 4 çalıştırılmadı (smoke'un amacı kurulum+eğitim yolu).

## SONUÇ (60/60 epoch, A100, 268 dk)

| metrik | değer |
|---|---|
| **ana skor — geçici yerel AP50 (maxDets=300)** | **0,59512** |
| AP50, maxDets=100 | 0,59206 |
| AP50:95 (maxDets=300) | 0,42258 |
| checkpoint | `best_stg2.pth`, epoch 59 |
| tahmin sayısı | 388.200 kutu / 1294 görüntü (görüntü başı tam 300 = D-FINE sorgu sayısı) |

### Sınıf başına AP50 — bir sonraki deneyi belirleyen bulgu
| sınıf | AP50 | val kutu payı |
|---|---|---|
| car | **0,8195** | %75,3 |
| bus | 0,6242 | %3,1 |
| van | 0,5273 | %14,0 |
| truck | **0,4094** | %7,7 |

**Tek bulgu:** truck (0,409) car'ın (0,820) yarısı. Ve bu saf sınıf dengesizliği değil —
bus yalnız %3,1 kutuya sahip ama 0,624 alıyor, truck %7,7 ile 0,409'da. Yani sorun örnek
sayısı değil, **truck/van/car ayrımı** görünüyor. Backlog'a bu gözlemle girer.

### maxDets kararı geriye dönük değerlendirme
maxDets 300 ile 100 arasındaki fark yalnız **0,0031** (0,59512 vs 0,59206). Kararın gerekçesi
doğruydu (val'de 7 görüntü–sınıf çifti 100'ü aşıyor) ama etkisi gürültü mertebesinde çıktı.

### D-00 ölçümü
200 px² altı tahmin: 9081 / 388.200 = **%2,3**. Filtrelenmedi. Resmi kuralın bunları nasıl
saydığı bilinmiyor; filtrelemenin etkisi ölçülmedi, backlog maddesi.

### Eğitim eğrisi (repo içi AP50, maxDets=100)
epoch 0: 0,005 · 5: 0,144 · 10: 0,265 · 20: 0,427 · 30: 0,508 · 40: 0,557 · 50: 0,580 · 59: 0,593.
Monoton, tıkanma yok. Son 10 epoch'ta epoch başına +0,0014 → **doymuş**. 51. epoch'taki
LR ×0,1 düşüşünde ve 53. epoch'ta augmentasyonun kapanmasında beklenen sıçrama **görülmedi**.

### A100 ölçümü (gözlem, epoch 0 tam)
| | T4, batch 8 | **A100-80GB, batch 32** |
|---|---|---|
| epoch süresi | 28,0 dk | **4,5 dk** (6,2× hızlı) |
| 60 epoch | 28,0 sa | **4,5 sa** |
| sn/adım | 1,708 | 1,067 (adım/epoch 646→161) |
| veri beklemesi | **%40** (2 vCPU) | **%8** (12 vCPU) — darboğaz kalktı |
| bellek zirvesi | 7,28 / 15,4 GB | 27,9 / 85,1 GB |
| AP50 (epoch 0) | 0,0077 | 0,0047 |

Epoch 0'da AP50 T4'ünkinden düşük: batch 32'de epoch başına 161 optimizer adımı var (T4'te 646)
ve warmup 2 epoch sürüyor. Epoch 0 değerleri gürültü seviyesinde, karşılaştırmaya girmez.

**Süre bütçesi çözüldü:** EXP-001 4,5 sa + EXP-002 (gürültü tabanı) 4,5 sa = 9 sa. İki güne sığar.

## T4 kısmi koşusu (iptal edildi, arşivlendi)
Tam veriyle 1 epoch koştu: **AP50 = 0,0077** · AP50:95 = 0,0029 (repo içi, maxDets=100).
Loss 29,70 → 23,68. Süre 28,0 dk/epoch → 60 epoch 28,0 sa; iki günlük yarışmaya sığmadı.
İnsan A100 + yüksek RAM'e geçti. **Devam edilmedi, sıfırdan başlatıldı** — batch 8→32 ve LR
birlikte değiştiği için devam eden koşu "1 epoch batch 8 + 59 epoch batch 32" olurdu:
tekrarlanamaz ve EXP-002 gürültü ikizi (K-09) üretilemez. Arşiv: `dfine_runs/EXP-001_t4_kismi_*`.

### Ölçülen hız (T4, batch 8, 960, sıfırdan)
| kaynak | eğitim sn/adım | not |
|---|---|---|
| SMOKE (256 görüntü) | 0,9123 | **YANILTICI** — 256 görüntü OS önbelleğine sığdığı için 2. epoch yapay hızlı |
| TAM koşu (5175 görüntü) | **1,708** | gerçek değer; `data: 0,68` → adımın **%40'ı veri beklemesi** |
| val | 0,5382 | smoke ölçümü |
| GPU bellek | 6927 / 15360 MiB | batch 16'ya yer var, denenmedi |

**T4'te gerçekleşen (gözlem, ekstrapolasyon değil): epoch 0 baştan sona 28,0 dk** → 60 ep = 28,0 sa.
Bellek zirvesi 7,28 GB / 15,4 GB.

> Süre tahmini iki kez yukarı revize edildi, ikisi de küçükten büyüğe ekstrapolasyondan:
> 11,3 sa (smoke'tan; 256 görüntü OS önbelleğine sığdı, dataloader gizlendi) → 19,9 sa
> (adım süresinden; val maliyeti 128 görüntülük smoke'tan alındığı için düşük çıktı) →
> **28,0 sa (ölçülen tam epoch)**. Ders: alt kümeden süre ekstrapole etme.

### Dataloader darboğazı (ölçüldü)
Veri: 6469 JPEG, 1,5 GB toplam, ortalama 0,24 MB, kaynak çözünürlük 1360×765 … 2000×1500.
Colab T4 runtime'ı **2 vCPU** veriyor, RAM 12 GB (7 GB önbellek boşta → disk I/O sorun değil,
**JPEG çözme + 960'a yeniden boyutlandırma + augmentasyon** sorun). `num_workers=2` tavan.

## Bu koşudan öğrenilen kod hataları (taslakta vardı, düzeltildi)
1. **`epoches` → `epochs`** (GEÇERSİZ KILAR, Codex Çağrı 1b buldu, repoda doğrulandı: `epoches`
   anahtarı repoda hiç geçmiyor). Düzeltilmeseydi 60 yerine config varsayılanı **220 epoch** koşardı.
2. **`HGNetv2.pretrained` repo varsayılanı `True`** (`configs/dfine/include/dfine_hgnetv2.yml`).
   Açıkça `False` yapılmazsa "sıfırdan" config'i bile ImageNet ağırlığını sessizce indirir → **D-03 ihlali**.
   Codex'in listesinde yoktu; repo okunarak bulundu. Artık `assert` ile korunuyor.
3. **`pgrep -f 'train.py -c'` kendi kabuğunu eşleştiriyor** — koşu yokken bile "ÇALIŞIYOR" derdi.
   Smoke'ta yakalandı, `[t]rain.py` desenine çevrildi.
4. **`ev.stats[0]` (AP50:95) `maxDets=[1,10,300]` ile −1 döner** (`_summarize` sabit 100 arar).
   `precision` dizisinden hesaplanıyor.
5. **SMOKE alt kümesi ilk N görüntüydü** → sınıf dengesi garantisiz. Sabit seed'li, her sınıftan
   en az 5 görüntü garantili örneklemeye çevrildi (ölçüldü: 4 sınıf da var).
6. **KX RESULT kapanış işareti uyumsuz:** kod `=== END KX RESULT ===` basıyordu,
   `kx.py` `RESULT_RE` tam olarak `=== KX RESULT SONU ===` arıyor → blok hiç bulunamıyordu.
   Taslaktan gelen hata, `kayit` denenince ortaya çıktı. Düzeltildi.
7. **Sabit `warmup_duration: 1000`** — A100'e geçip batch büyüyünce adım/epoch 646'dan 161'e
   düştü, 1000 iter 6,2 epoch warmup demek olurdu (batch 48'de 9,3). Repoda doğrulandı: warmup
   iterasyon cinsinden adımlanıyor ve `lr_scheduler` warmup bitene kadar hiç adımlamıyor.
   Artık `2 × adım/epoch` ve bütçenin %10'unu aşarsa `assert` düşüyor.

## OOF HATA ANALİZİ (26 Eyl) — kod: `hata_analizi.py`
Sınıf başına AP'nin ayırmadığı şeyi ayırmak için: kayıp **karışıklık** mı, **kaçırma** mı?

**Karışıklık matrisi** (IoU≥0,5, skor≥0,30, sınıf-bağımsız eşleştirme):

| GT \ tahmin | car | van | truck | bus | KAÇIRILDI | toplam |
|---|---|---|---|---|---|---|
| car | 20.849 | 779 | 71 | 17 | 2.626 | 24.342 |
| van | **1.786** | 1.937 | 157 | 34 | 607 | 4.521 |
| truck | 339 | 155 | 1.141 | 156 | **686** | 2.477 |
| bus | 28 | 38 | 152 | 634 | 151 | 1.003 |

| sınıf | doğru | yanlış sınıf | kaçırıldı |
|---|---|---|---|
| car | %85,7 | %3,6 | %10,8 |
| van | %42,8 | **%43,7** | %13,4 |
| truck | %46,1 | %26,2 | **%27,7** |
| bus | %63,2 | %21,7 | %15,1 |

**Küçük nesne (<32²) kaçırma oranı:** car %19,3 (n=9539) · van %24,1 (n=1699) ·
**truck %35,3** (n=674) · bus %23,8 (n=256).

### İki ayrı problem, farklı çözüm ister
1. **van → car (1.786 kutu = van'ın %39,5'i).** Matristeki en büyük köşegen-dışı hücre.
   Asimetrik: ters yön 779. Model şüphede car'a kayıyor — car kutuların %75'i olduğu için beklenir.
   Bu bir **sınıflandırma** problemi; nesne bulunuyor, kutu doğru, etiket yanlış.
2. **truck kaçırma %27,7** (car'ın 2,5 katı), küçük truck'larda **%35,3**.
   Bu bir **tespit/çözünürlük** problemi, sınıflandırma değil.

### Neden skoru bu kadar vuruyor
mAP@0.5 dört sınıfı eşit ağırlıklandırıyor: van kutuların %14'ü ama skorun %25'i, truck %7,7 ama
yine %25. car'ı iyileştirmek neredeyse boşa; van/truck doğrudan skor.

### Yöntem uyarısı
Eşleştirme COCO'nun resmi eşleştirmesi **değil**: açgözlü, GT sırasına göre (güvene göre değil),
sınıf-bağımsız (karışıklığı görebilmek için kasten) ve tek skor eşiği (0,30). Oranlar eşiğe
duyarlı. Yön güvenilir, ondalıklar yaklaşık. **Skor olarak raporlanmaz, hipotez üretir.**

## Gönderim
**Gönderilmedi.** K-01 gereği Kaggle'a hiçbir şey gönderilmiyor; K-04 gereği akışta zorunlu
submission yok. `log/SUBMISSIONS.md` boş kalıyor. Bu koşu yalnız yerel ölçüm zemini.

## Ağırlıklar ve disk (26 Eyl)
Korunan: `dfine_runs/EXP-001/` → `best_stg2.pth` (165,5 MB, **epoch 59, skorlanan model**) ·
`best_stg1.pth` · `last.pth` · `val_dets.json` (145,6 MB, kural 5: tahmin silinmez) · loglar.
**Ağırlıklar git'te değil, yalnız Drive'da** — Aşama 2 agent'ı bu dedektörü kullanacak.

**Silinen:** 53 × `checkpointNNNN.pth` = **8,77 GB** (insan onayıyla). `dfine_runs` 11 GB → 2,1 GB.
Analitik değerleri yoktu: kayıtta AP50 epoch 59'a kadar monoton arttı, yani en iyi AP50 epoch'u
zaten son epoch ve `best_stg2.pth` onu tutuyor.

**Bu israf bir kod hatasıydı:** `checkpoint_freq` taslakta 1000'ken 1'e çekilmişti, gerekçe
"oturum koparsa devam". Ama `last.pth` zaten her epoch **koşulsuz** yazılıyor
(`src/solver/det_solver.py:100`); `checkpoint_freq` yalnız numaralı kopyaları üretiyor.
Kodda 1000'e geri alındı. Değiştirmeden önce repo okunmalıydı.

### Kapanan risk
"En iyi checkpoint AP50:95'e göre seçiliyor, ana skorumuz AP50, çakışmayabilir" riski
**kapandı**: AP50 monoton arttığı için iki ölçütün en iyisi aynı epoch (59).

## Riskler (ölçülebilir, koşuyu geçersiz kılmaz)
- **En iyi checkpoint AP50:95'e göre seçiliyor** (`src/solver/det_solver.py`), ana skorumuz AP50.
  En iyi AP50 epoch'uyla çakışmayabilir. Ölçülmedi.
- **60 epoch, repo sıfırdan tarifinin (220) %27'si.** Model eksik eğitilmiş olacak. Süre bütçesi kararı.
  LR milestone 51. epoch'ta (%85) düşüyor — koşu sonradan uzatılırsa LR zaten düşmüş olur.
- **Süre bütçesi ÇAKIŞIYOR.** 60 epoch = 19,9 sa. `EXP-002` (gürültü tabanı, K-09) aynı kodun
  yalnız SEED'i değişmiş hâli → bir 19,9 sa daha. Toplam ≈40 sa, yarışma iki gün. İnsan kararı bekliyor.
- **Colab oturumu kopabilir.** `checkpoint_freq: 1` ile her epoch `last.pth` Drive'a yazılıyor,
  hücre 2 `-r last.pth` ile devam eder.
- **Yakın-kopya sızıntısı dışlanmadı** (Codex Çağrı 1). D-01 değişmiyor (kural 1: kanıtlanmış kusur yok),
  kontrol `log/BACKLOG.md`'ye girer.
- **Skor "geçici yerel AP50"**: resmi scorer'ın interpolasyonu, tespit sınırı ve "200 px² altı puanı
  etkilemez" kuralının nasıl işlendiği bilinmiyor (`case/CASE.md` satır 2 ENGEL).
- D-00 (200 px² altı) çıktıda **filtrelenmiyor**, yalnız oranı ölçülüp raporlanıyor.

## Atlanan doğrulama
- **`python tools/kx.py kayit EXP-001` KOŞTURULDU ve REDDETTİ.** Tahmin değil, ölçülen çıktı:
  ```
  DOGRULAMA BASARISIZ - sonuc kayda GIRMEDI:
    - result.json: 'exp_id' alani yok
    - result.json: 'cv_mean' alani yok
    - result.json: 'cv_oof' alani yok
    - result.json: 'fold_scores' alani yok
    - result.json: 'n_folds_done' alani yok
    - result.json: 'mode' alani yok (FAST/FULL ayrimi yapilamaz)
  ```
  Sebep: doğrulayıcı tablo şeması bekliyor, tespit sonucu tek holdout (fold yok).
  `core/cv_spec.md` hâlâ BOŞ — D-01'de doldurulmamış, yani uyulacak bir çıktı sözleşmesi yok.
  EXP-001 sonucu `card.md` + `log/RUNS.md` + `EXP_SUMMARY.md`'ye **elle** yazıldı.
  **İnsan kararı bekliyor:** tek holdout'u `fold_scores=[AP50]`, `n_folds_done=1`,
  `cv_mean=cv_oof=AP50`, `mode="FULL"` diye eşlemek sözleşmeyi açar ve `cmp` gürültü tabanıyla
  (K-09) çalışır. Bu eşlemeyi tek başıma yapmadım; `cv_spec.md` D-01 artefaktı.
- `tools/adv_val.py` (test-ayrım kanıtı) koşturulmadı — tablo varsayıyor, Kaggle test seti de yok.
- Ürün etkisi notu: model çıktısı kutu merkezi koruyor (Aşama 2 piksel→koordinat için gerekli), ölçülmedi.
