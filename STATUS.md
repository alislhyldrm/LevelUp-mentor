# STATUS — Level Up AI / ROKETSAN Aşama 1 (araç tespiti, D-FINE)
<!-- Oturum devir dosyası. Yeni oturum önce bunu okur. Append edilmez, yeniden yazılır. -->

## İnsandan sıradaki eylem
→ (1) **ONAY: EXP-002 gürültü koşusu başlasın mı?** Aynı kod, yalnız `SEED=1`, 4,5 sa.
  K-09 gereği; onsuz KABUL/RED kararları gürültüye açık kalır.
  (2) **KARAR: çıktı sözleşmesi.** `kx.py kayit` tespit sonucunu reddediyor. Tek holdout'u
  `fold_scores=[AP50]`, `n_folds_done=1`, `cv_mean=cv_oof=AP50`, `mode=FULL` diye eşleyip
  `core/cv_spec.md`'yi dolduralım mı? Tek başıma yapmadım — D-01 artefaktı.
  (3) Açık: Kaggle Rules (Colab'da eğitim izni, ağırlığı taşıma, submission formatı).

## Şu an
Faz: baseline bitti | **Ana hat: EXP-001, AP50 0,59512** | Son kontrol: 26 Eyl, 60/60 epoch
Colab'da koşan: yok · Kaggle'da koşan: yok (K-01)

## Sıradaki 3 iş
1. EXP-002 gürültü koşusu (`SEED=1`) — 4,5 sa, onay bekliyor
2. OOF hata analizi + Codex Çağrı 4 → `log/BACKLOG.md` doldur
3. ✋Onay 2 (baseline + gürültü tabanı + hata analizi + dolu backlog, tek pakette)

## EXP-001 sonucu (ana hat) — ayrıntı `experiments/EXP-001/card.md`
**AP50 = 0,59512** (geçici yerel, COCO maxDets=300, 4 sınıf ort.) · AP50:95 = 0,42258 ·
AP50@100 = 0,59206 · 60/60 epoch, 268 dk, ckpt `best_stg2.pth` (ep 59).
Kurulum: D-FINE-S sıfırdan, 960, batch 32, lr 2,828e-4, A100-80GB.
**Sınıf başına AP50: car 0,820 · bus 0,624 · van 0,527 · truck 0,409.**
→ **Tek bulgu:** truck car'ın yarısı — ama bus yalnız %3,1 kutuyla 0,624 alıyor. Sorun örnek
sayısı değil, **truck/van/car ayrımı**. Bir sonraki deneyi bu belirlemeli.
Eğri son 10 ep'ta +0,0014/ep → doymuş. maxDets 300↔100 farkı 0,0031. 200 px² altı tahmin %2,3.

## Bu oturumda ne oldu
- **D-05 (insan): Obj365 ağırlığı YASAK** → sıfırdan eğitim, model M→S.
- **Codex Çağrı 1 + 1b** koştu; bulguları repoda doğrulandı. Taslakta 7 hata bulunup düzeltildi
  (tam liste `card.md`): en ağırı `epoches`→`epochs` ve `HGNetv2.pretrained` varsayılanı `True`
  (sıfırdan config bile ImageNet indirirdi = **D-03 ihlali**). Hepsi artık `assert`le korunuyor.
- **Donanım:** T4 (2 vCPU) 28 dk/epoch → 28 sa, sığmadı. İnsan **A100-80GB (12 vCPU)**'ya geçti:
  4,5 dk/epoch. T4'ün 1 epoch'u arşivlendi (`EXP-001_t4_kismi_2149`), devam EDİLMEDİ (batch+LR değişti).
- **Süre tahmini üç kez yukarı revize edildi** (11,3→19,9→28,0 sa), hepsi alt kümeden
  ekstrapolasyon hatasıydı. **Ders: alt kümeden süre ekstrapole etme, tam epoch ölç.**
- **Codex modeli:** `gpt-6-sol` hesapta yok (`~/.codex/config.toml` yazım hatası, `gpt-5.6-sol`
  olmalı). **TPU uygun değil:** DETR değişken kutu sayısı + Hungarian → XLA sabit şekil ister.

## Önceki oturum
- D-01…D-04; EDA bitti, split JSON + zip hazır, Colab MCP kuruldu.
- Ana EDA bulgusu: kutuların %38'i <32² → 960 giriş gerekli, 640 yetmez.

## Öncesi
- Resmi PDF (mAP@0.5, 4 sınıf, 5/gün, toplam 10, final 2); kurulum ve prova K-01…K-09.

## Sabitlenen kararlar
- K-01…K-09: Kaggle'a gönderim yok · her koşu kendi onayı · zorunlu submission yok · gürültü tabanı.
- D-00: 200 px² altı hedeflenmez · D-01: tek bölme, ana skor val mAP@0.5 · D-02: koşuyu ajan yapar
  · D-03: dış veri yasak · **D-05: sıfırdan eğitim** (ImageNet backbone de yasak).
- Bölme izi: train `3214f3fa7f9abfe8` (5175/132.989) · val `209e9c83a27b935c` (1294/32.343).

## Denendi, işe yaramadı
- **51. epoch LR ×0,1 düşüşü ve 53. epoch augmentasyon kapanması** — ikisinde de beklenen AP
  sıçraması olmadı, eğri düz devam etti. Doymuş eğride bu kaldıraçlar işe yaramıyor.

## Aktif riskler
- **`kx.py kayit` tespit sonucunu REDDEDİYOR** (koşuldu): `exp_id`/`cv_mean`/`cv_oof`/`fold_scores`/
  `n_folds_done`/`mode` yok, `cv_spec.md` boş. EXP-001 elle kaydedildi. Eşleme önerisi onayda.
- **60 epoch = repo sıfırdan tarifinin %27'si.** Eğri doymuş görünüyor ama gerçekten mi, yoksa LR
  düşüşü mü erken geldi — ölçülmedi.
- **Yakın-kopya sızıntısı dışlanmadı** (Codex Çağrı 1). D-01 değişmiyor (kural 1), kontrol backlog'a.
- **Skor "geçici yerel AP50"** — resmi scorer'ın interpolasyon/sınır/ignore davranışı bilinmiyor.
- En iyi ckpt AP50:95'e göre seçiliyor (ana skor AP50) · Colab kopabilir (ckpt Drive'da) ·
  Evren verisi–Kaggle train ilişkisi bilinmiyor.

## Ürüne taşınabilecek en güçlü 3 bulgu
1. **truck/van ayrımı zayıf** (0,409 / 0,527 vs car 0,820) ve bu örnek sayısından değil — ölçüldü.
2. Küçük nesne baskın (%38 <32²) → çözünürlük kararı skoru belirler (hipotez, ölçülmedi).
3. 960'ta dataloader vCPU'ya bağlı: 2 vCPU'da adımın %40'ı bekleme, 12 vCPU'da %8 — ölçüldü.

## Yarışma öncesi kontrol listesi
- [ ] Kaggle Data/Rules · [x] GPU (A100-80GB, 12 vCPU) · [x] D-01 split + parmak izi doğrulanıyor
