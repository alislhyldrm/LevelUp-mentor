# Metrik kataloğu

Yarışmanın resmi metni ve kodu her zaman bu katalogdan üstündür. Katalog, sözleşmenin boş alanlarını doldurmak ve tuzakları hatırlamak içindir.

**Kaynak etiketleri**
- **[SK]** scikit-learn model evaluation dokümanı: https://scikit-learn.org/stable/modules/model_evaluation.html
- **[V]** Yerel doğrulama: scikit-learn 1.9.1, 19 Eylül 2026 (sayısal deney; sonuç satırda).
- **[COCO]** COCO detection değerlendirmesi: https://cocodataset.org/#detection-eval
- **[BH]** Ben Hamner, Kaggle metrik uygulamaları: https://github.com/benhamner/Metrics
- **TAHMİN**: doğrulanmadı; yarışma metninden kontrol et.

Alanlar: **Ne ölçer** · **Yön** · **Girdi** · **En iyi sabit tahmin** (taban skor) · **Tuzak** · **Metriğe göre hamle** (fikir kuyruğuna hipotez) · **sklearn**.

---

## Sınıflandırma

### 1. Accuracy
- Ne ölçer: doğru tahmin oranı. Yön: büyük. Girdi: etiket.
- En iyi sabit: çoğunluk sınıfı; skor = çoğunluk oranı. [V: %38,2 çoğunluklu 5 sınıfta 0,382]
- Tuzak: dengesiz veride azınlık sınıfı hiç bilinmeden yüksek çıkar.
- Hamle: olasılıktan argmax; eşik ayarı genelde gerekmez.
- sklearn: `accuracy_score` [SK]

### 2. Precision ve recall
- Ne ölçer: precision = TP / (TP + FP), "pozitif dediklerimin ne kadarı doğru"; recall = TP / (TP + FN), "gerçek pozitiflerin ne kadarını yakaladım". Yön: büyük. Girdi: etiket (eşiklenmiş).
- En iyi sabit: hepsine pozitif → recall 1, precision = pozitif oranı.
- Tuzak: paydalar farklı; biri tek başına optimize edilirse diğeri çöker. Kaçırmak pahalıysa recall, yanlış alarm pahalıysa precision öne çıkar.
- Hamle: eşik (OOF üzerinde).
- sklearn: `precision_score`, `recall_score` [SK]

### 3. F1 (binary, macro, micro, weighted)
- Ne ölçer: F1 = 2PR / (P + R). **Macro:** her sınıfın F1'i, ağırlıksız ortalama; nadir sınıf çoğunluk sınıfıyla eşit ağırlıkta. **Micro:** bütün TP/FP/FN toplanır; tek etiketli çok sınıfta accuracy'ye eşittir [V: örnekte ikisi de 0,6]. **Weighted:** sınıf F1'leri sınıf büyüklüğüyle ağırlıklı.
- Yön: büyük. Girdi: etiket.
- En iyi sabit: binary'de hepsine pozitif → 2p / (1 + p), p = pozitif oranı [V: p=0,104 → 0,188]. Macro'da çoğunluk sınıfı → yalnız o sınıfın F1'i / sınıf sayısı [V: 5 sınıf, çoğunluk %38,2 → 0,111; aynı tahminin accuracy'si 0,382].
- Tuzak: varyantı yanlış seçmek; macro'da nadir sınıfı ihmal etmek; `zero_division` davranışı (hiç tahmin edilmeyen sınıfın F1'i 0).
- Hamle: sınıf ağırlığı; sınıf bazlı eşik ya da olasılık ölçekleme (OOF üzerinde); macro'da nadir sınıfın recall'unu artırmak.
- sklearn: `f1_score(average="binary"|"macro"|"micro"|"weighted")`, `fbeta_score` [SK]

### 4. ROC AUC
- Ne ölçer: rastgele bir pozitifin rastgele bir negatiften yüksek skor alma olasılığı; yalnız **sıralamaya** bakar. Yön: büyük. Girdi: skor/olasılık (etiket değil).
- En iyi sabit: her sabit 0,5 [V]. Monoton dönüşüm skoru değiştirmez [V: s ve s³ aynı AUC].
- Tuzak: sert etiket (0/1) göndermek skoru düşürür; kalibrasyon önemsizdir; çok sınıfta OvR/OvO ve ortalama türü yarışmaya göre değişir.
- Hamle: modelleri olasılık yerine **sıra ortalamasıyla** (rank averaging) birleştirmek.
- sklearn: `roc_auc_score(multi_class="ovr"|"ovo")` [SK]

### 5. PR AUC / Average Precision (AP)
- Ne ölçer: precision-recall eğrisinin özeti; dengesiz veride pozitif sınıfa odaklıdır. Yön: büyük. Girdi: skor/olasılık.
- En iyi sabit: pozitif oranı [V: 0,104 prevalansta 0,104].
- Tuzak: ROC AUC ile aynı şeyi söylemez; nadir pozitifte ROC yüksekken AP düşük olabilir. "PR AUC" (yamuk integral) ile AP (basamaklı toplam) sayısal olarak farklıdır.
- Hamle: pozitif sınıfın sıralamasını iyileştirmek; rank averaging.
- sklearn: `average_precision_score` [SK]

### 6. Log loss (cross-entropy)
- Ne ölçer: doğru sınıfa verilen olasılığın −log ortalaması; emin ama yanlış tahmini çok ağır cezalandırır. Yön: küçük. Girdi: sınıf olasılıkları (sütun sırası önemli).
- En iyi sabit: sınıf öncül oranları [V: %10 pozitifte öncül 0,322; 0,5 sabit 0,693].
- Tuzak: tek bir emin-yanlış tahmin ortalamayı patlatır [V: p=1e-15 ile tek satır 34,5]; olasılık yerine etiket göndermek; sınıf sütun sırası.
- Hamle: olasılıkları [ε, 1−ε] aralığına kırpmak (clipping), kalibrasyon (temperature/isotonic), olasılık ortalamasıyla ensemble. Kaggle'ın clipping değeri: TAHMİN, Evaluation'dan kontrol et. scikit-learn 1.9'da `log_loss` fonksiyonunun `eps` parametresi yok [V].
- sklearn: `log_loss` [SK]

### 7. MCC (Matthews korelasyon katsayısı)
- Ne ölçer: gerçek ile tahmin arasındaki korelasyon; dört hücrenin (TP, TN, FP, FN) hepsini kullanır. Aralık −1..1. Yön: büyük. Girdi: etiket.
- En iyi sabit: 0 [V].
- Tuzak: eşik seçimine çok duyarlı.
- Hamle: eşik (OOF üzerinde).
- sklearn: `matthews_corrcoef` [SK]

### 8. QWK (quadratic weighted kappa)
- Ne ölçer: sıralı sınıflarda uyum; uzak hataları karesiyle cezalandırır (1 yerine 4 demek, 1 yerine 2 demekten çok daha kötü). Aralık −1..1. Yön: büyük. Girdi: sıralı etiket.
- En iyi sabit: 0 [V].
- Tuzak: sınıflandırıcı gibi eğitip sıralamayı yok saymak.
- Hamle: regresyon gibi eğitip sürekli çıktıyı **eşiklerle** sınıfa yuvarlamak; eşikleri OOF üzerinde optimize etmek.
- sklearn: `cohen_kappa_score(weights="quadratic")` [SK] [V: [0,1,2,3] vs [0,2,2,3] → 0,9]

---

## Regresyon

### 9. MAE
- Ne ölçer: ortalama mutlak hata; hedefin biriminde. Yön: küçük. Girdi: sayı.
- En iyi sabit: **medyan** [V].
- Tuzak: MSE loss ile eğitmek ortalamaya yöneltir, MAE medyanı ister.
- Hamle: L1 / MAE loss; aykırı değere dayanıklı model.
- sklearn: `mean_absolute_error` [SK]

### 10. RMSE (ve MSE)
- Ne ölçer: hata karelerinin ortalamasının karekökü; büyük hataları büyütür. Yön: küçük. Girdi: sayı.
- En iyi sabit: **ortalama** [V].
- Tuzak: tek büyük hata skoru domine eder; her satırın kökünü alıp ortalamak yanlış formüldür.
- Hamle: MSE loss; aykırı değer analizi; fold'larda RMSE'yi yeniden hesapla, fold RMSE'lerinin ortalaması toplam RMSE'ye eşit değildir.
- sklearn: `root_mean_squared_error`, `mean_squared_error` [SK]

### 11. RMSLE
- Ne ölçer: log(1 + y) uzayında RMSE; oransal hatayı ölçer, küçük değerleri korur. Yön: küçük. Girdi: negatif olmayan sayı.
- En iyi sabit: expm1(ortalama(log1p(y))) [V].
- Tuzak: negatif tahmin hata verir [V: ValueError]; ham hedefle MSE eğitmek yanlış şeyi optimize eder.
- Hamle: hedefi `log1p` ile dönüştürüp RMSE eğitmek, tahmini `expm1` ile geri çevirmek; negatif tahmini 0'a kırpmak.
- sklearn: `root_mean_squared_log_error` [SK]

### 12. MAPE ve SMAPE
- Ne ölçer: MAPE = ortalama |y − ŷ| / |y|, oransal hata. Yön: küçük. Girdi: sayı.
- Tuzak: scikit-learn **oran** döndürür, yüzde değil [V: 100→110 için 0,1]; gerçek değer 0 iken patlar [V: ~2,25e15]; düşük tahmini az, yüksek tahmini çok cezalandırır. SMAPE'nin birden çok tanımı var: TAHMİN, yarışma formülünü birebir al.
- Hamle: sıfıra yakın hedefleri ayrı ele almak; oransal hataya uygun loss.
- sklearn: `mean_absolute_percentage_error`; SMAPE yok, elle yazılır [SK]

### 13. R²
- Ne ölçer: modelin, sabit ortalama tahminine göre açıkladığı varyans oranı. Yön: büyük; en iyi 1.
- En iyi sabit: ortalama → 0 [V]. Kötü model **negatif** olur [V: −3,0].
- Tuzak: fold bazında R² ile toplam R² farklı; farklı veri setlerinde karşılaştırılamaz.
- sklearn: `r2_score` [SK]

---

## Sıralama ve tespit

### 14. MAP@K
- Ne ölçer: her sorgu için ilk K tahminin ortalama kesinliği (average precision), sonra sorgular üzerinden ortalama. Yön: büyük. Girdi: sıralı tahmin listesi (en fazla K).
- En iyi sabit: herkese en popüler K öğe (sezgisel taban).
- Tuzak: listede tekrar eden öğe; K'dan uzun liste; paydanın min(K, gerçek öğe sayısı) olması. Tanım yarışmaya göre değişebilir: TAHMİN.
- Hamle: popülerlik tabanını her zaman listenin sonuna eklemek.
- sklearn: yok. Referans uygulama: `apk`/`mapk` [BH]

### 15. Tespit: IoU ve mAP
- **IoU** = kesişim / birleşim (kutu ya da maske). Segmentasyonda Dice = 2·kesişim / (A + B); ikili maskede Dice = F1 [V: jaccard 0,5, dice 0,667].
- **mAP:** her sınıf için, IoU eşiğini geçen tahminlerle hesaplanan AP'nin ortalaması. **mAP@0.5** tek eşik (0,5); **mAP@[.5:.95]** 0,50'den 0,95'e 0,05 adımla 10 eşiğin ortalaması (COCO ana metriği) [COCO]. İkisi aynı metrik değildir.
- Yön: büyük. Girdi: kutu + sınıf + güven skoru.
- Tuzak: kutu biçimi karışıklığı (`xyxy` / `xywh` / merkez-`cxcywh`, piksel / normalize); güven skorunu göndermemek; düşük güvenli kutuları erken kesmek (mAP çok sayıda düşük güvenli kutudan zarar görmeyebilir: TAHMİN, resmi koda bak).
- Hamle: NMS/IoU eşiği ve güven eşiği ayarı (OOF/validasyon üzerinde); test-time augmentation.
- sklearn: `jaccard_score` (IoU için); mAP için pycocotools ya da kullanılan kütüphanenin değerlendiricisi (ör. Ultralytics `val`).
