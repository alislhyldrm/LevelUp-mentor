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
| durum | **SMOKE geçti · tam koşu başladı, sonuç bekleniyor** |

## Dört satır
- **Hangi backlog maddesi:** — (ilk baseline)
- **Hipotez:** 960 girişte sıfırdan eğitilmiş D-FINE-S, bu veride ölçülebilir bir mAP@0.5 zemini verir.
- **Dayanak:** EDA — kutuların %38'i <32², 640'a küçültünce p5 kutu kenarı ≈ 7 px (`case/CASE.md` satır 6).
- **Tahmini süre:** ÖLÇÜLDÜ (tam koşu) → 19,9 dk/epoch × 60 epoch ≈ **19,9 saat**.

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
6. **Sabit `warmup_duration: 1000`** — A100'e geçip batch büyüyünce adım/epoch 646'dan 161'e
   düştü, 1000 iter 6,2 epoch warmup demek olurdu (batch 48'de 9,3). Repoda doğrulandı: warmup
   iterasyon cinsinden adımlanıyor ve `lr_scheduler` warmup bitene kadar hiç adımlamıyor.
   Artık `2 × adım/epoch` ve bütçenin %10'unu aşarsa `assert` düşüyor.

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
- **`python tools/kx.py kayit EXP-001` koşturulamadı.** Altyapı hâlâ tablo şemasında:
  `core/cv_spec.md` boş (D-01'de doldurulmamış), `kx.json` `main_score: "cv_mean"`, `validate_output`
  `fold_scores` / `cv_oof` / `fold_fingerprint` bekliyor. Tespit sonucu bu sözleşmeye uymuyor
  (tek holdout, fold yok, ana skor AP50). `case/CASE.md`'deki insan kararı: altyapı case'e göre
  yeniden kurulacak. Bu yapılana kadar EXP-001 sonucu `card.md` + `log/RUNS.md`'de elle tutuluyor.
- `tools/adv_val.py` (test-ayrım kanıtı) koşturulmadı — tablo varsayıyor, Kaggle test seti de yok.
- Ürün etkisi notu: model çıktısı kutu merkezi koruyor (Aşama 2 piksel→koordinat için gerekli), ölçülmedi.
