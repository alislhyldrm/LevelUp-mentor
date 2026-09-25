# STATUS — Level Up AI / ROKETSAN Aşama 1 (araç tespiti, D-FINE)
<!-- Oturum devir dosyası. Yeni oturum önce bunu okur. Append edilmez, yeniden yazılır. -->

## İnsandan sıradaki eylem
→ (1) Colab sekmesini **açık tut** — EXP-001 A100'de koşuyor, tahmini bitiş **4,5 sa**.
  Kopar ise hücre 0 (Drive) → 1 → 2 (`-r last.pth` ile otomatik devam).
  (2) Compute unit tüketimini izle; A100 hızlı harcar.
  (3) Açık: Kaggle Rules (Colab'da eğitim izni, ağırlığı taşıma, submission formatı).

## Şu an
Faz: baseline koşuyor | Ana hat: yok (EXP-001 ilk) | Son kontrol: 26 Eyl, epoch 1/60 bitti
Colab'da koşan: EXP-001 (**A100-80GB**, 4,5 dk/epoch) · Kaggle'da koşan: yok (K-01)

## Sıradaki 3 iş
1. EXP-001 bitince hücre 4 → KX RESULT → `card.md` + `log/RUNS.md`
2. EXP-002 gürültü koşusu (aynı kod, farklı SEED) — 4,5 sa, bütçeye sığıyor
3. OOF hata analizi + `log/BACKLOG.md` → ✋Onay 2

## Bu oturumda ne oldu
- **D-05 (insan): Objects365 ağırlığı YASAK** → EXP-001 sıfırdan eğitime çevrildi, model M→S.
- **Codex Çağrı 1 + 1b koştu;** 1b dört "GEÇERSİZ KILAR" verdi, hepsi gerçek repoda doğrulanıp
  düzeltildi: `epoches`→`epochs` (yoksa 220 epoch koşardı) · `HGNetv2.pretrained` varsayılanı `True`
  → "sıfırdan" config bile ImageNet indirirdi (**D-03 ihlali**), artık `assert` · `pgrep` kendi
  kabuğunu eşleştiriyordu (hep "ÇALIŞIYOR") · `ev.stats[0]` maxDets=300'de −1 · SMOKE ilk-N →
  sınıf garantili örnekleme · 640→960 regex yerine yapılandırılmış override + DOĞRULA assert'leri.
- **GPU: Tesla T4 15,6 GB, 2 vCPU, 12 GB RAM.** Bellek 6,9/15,4 GB → batch 16'ya yer var, denenmedi.
- **SMOKE geçti** (256/128, 2 ep): DOĞRULA tam. **Tam koşu başladı:** D-FINE-S sıfırdan, 960, batch 8,
  60 ep, lr 1,414e-4 (sqrt ölçekleme).
- **Süre tahminleri üç kez yukarı revize edildi** (11,3 → 19,9 → 28,0 sa), hepsi alt kümeden
  ekstrapolasyon hatasıydı. **Ders: alt kümeden süre ekstrapole etme, tam epoch ölç.**
- **T4'te gerçek: 28,0 dk/epoch, AP50(1 ep) 0,0077.** 28 sa iki güne sığmadı → insan A100'e geçti.
- **A100-SXM4-80GB (85 GB, 12 vCPU): 4,5 dk/epoch → 60 epoch = 4,5 sa.** 6,2× hızlı.
  Veri beklemesi %40 → **%8** (12 vCPU darboğazı kaldırdı). Bellek 27,9/85,1 GB.
  **Süre bütçesi çözüldü:** EXP-001 4,5 sa + EXP-002 4,5 sa = 9 sa, iki güne sığar.
- **Yeni hata bulundu:** `warmup_duration` İTERASYON cinsinden (`det_engine.py:119`) ve
  `lr_scheduler` warmup bitene kadar hiç adımlamıyor (`det_solver.py:94`). Sabit 1000 iter,
  batch 32'de 6,2 epoch warmup demekti. Artık `2 × adım/epoch`, %10 aşımında `assert`.
- **T4 koşusu arşivlendi, devam EDİLMEDİ** (`EXP-001_t4_kismi_2149`): batch 8→32 ve LR birlikte
  değişti; devam eden koşu tekrarlanamaz olur ve EXP-002 gürültü ikizi (K-09) üretilemezdi.
- **TPU: hayır.** D-FINE saf PyTorch/CUDA; DETR değişken kutu sayısı + Hungarian → XLA sabit şekil
  ister, her adımda yeniden derler. **Codex modeli:** `gpt-6-sol` hesapta yok (config.toml yazım
  hatası); kullanılabilir `gpt-6-astra`, `gpt-5.6-sol/terra/luna`, `gpt-5.5`.
- Parmak izi: train 5175/132.989 `3214f3fa7f9abfe8` · val 1294/32.343 `209e9c83a27b935c` · kesişim 0.
  `maxDets=300` gerekçesi düzeltildi: COCO sınırı görüntü**×sınıf** başına, val'de 7 çift aşıyor.

## Önceki oturum
- D-01…D-04 alındı; EDA bitti, split JSON + zip hazır, Colab MCP kuruldu.
- Ana EDA bulgusu: kutuların %38'i <32² → 960-1280 giriş gerekli, 640 yetmez.

## Öncesi
- Resmi PDF (mAP@0.5, 4 sınıf, 5/gün, toplam 10, final 2); kurulum ve prova K-01…K-09.

## Sabitlenen kararlar
- K-01…K-09: Kaggle'a gönderim yok · her koşu kendi onayı · zorunlu submission yok · gürültü tabanı.
- D-00: 200 px² altı hedeflenmez (filtrelenmiyor, oranı ölçülüyor) · D-01: tek bölme, ana skor val
  mAP@0.5 · D-02: koşuyu ajan yapar · D-03: dış veri yasak · **D-05: sıfırdan eğitim.**

## Denendi, işe yaramadı
- (yok — ilk baseline henüz bitmedi)

## Aktif riskler
- **60 epoch = repo sıfırdan tarifinin %27'si** → eksik eğitim. LR milestone 51'de düşüyor; uzatmak bedava değil.
- **`kx.py kayit` koşturulamıyor:** altyapı tablo şemasında (`cv_spec.md` boş, `fold_scores` bekleniyor);
  EXP-001 elle `card.md` + `RUNS.md`'de.
- **Yakın-kopya sızıntısı dışlanmadı** (Codex Çağrı 1). D-01 değişmiyor (kural 1), kontrol backlog'a.
- **Skor "geçici yerel AP50"** — resmi scorer'ın interpolasyon/sınır/ignore davranışı bilinmiyor.
- **En iyi checkpoint AP50:95'e göre seçiliyor**, ana skor AP50. Çakışmayabilir, ölçülmedi.
- Colab kopabilir (checkpoint Drive'da) · Evren verisi–Kaggle train ilişkisi bilinmiyor · bus %3,4.

## Ürüne taşınabilecek en güçlü 3 bulgu
1. Küçük nesne baskın (%38 <32²) → çözünürlük kararı skoru belirler (hipotez, ölçülmedi).
2. 960 çözünürlükte dataloader vCPU'ya bağlı: 2 vCPU'da adımın %40'ı bekleme, 12 vCPU'da %8 — ölçüldü.
3. —

## Yarışma öncesi kontrol listesi
- [ ] Kaggle Data/Rules · [x] GPU ölçüldü (T4, 2 vCPU) · [x] D-01 split + parmak izi doğrulanıyor
