# CASE — Level Up AI | ROKETSAN Yapay Zekâ Hackathonu (Aşama 1: araç tespiti)

> `/case` doldurur. Ham sayfa metinleri `case/pages/` altındadır — çelişkide **ham metin hakemdir.**
> Kaggle sayfaları login arkasındadır; Overview · Data · Evaluation · Rules metnini **insan yapıştırır.**
> Cevaplanamayan satır boş bırakılmaz: **ENGEL — bilinmiyor + nasıl öğrenilecek** yazılır.
>
> Kaynak kısaltması: **BD** = `case/pages/bilgilendirme-dokumani-1448.md` (resmi PDF, sayfa 2-4 + SSS görüldü;
> sayfa 1 ve 5 görülmedi; insan: kayda değer bilgi yok). Kaggle sayfaları henüz gelmedi.

## Triyaj (ilk 10 dakika — bunlar bilinmeden kod yazılmaz)

| # | Soru | Cevap | Kaynak |
|---|---|---|---|
| 1 | Code competition mı (notebook submission)? | **ENGEL — bilinmiyor.** BD "final notebook'u Coderspace ve ROKETSAN ile paylaşın" diyor ama submission'ın CSV mi notebook çıktısı mı olduğunu söylemiyor. Kaggle Overview/Rules sayfasından öğrenilir | BD s.3 |
| 2 | Metrik ve yönü | **mAP@0.5**, büyük iyi. Sınıf doğru + IoU ≥ 0.5 ise doğru tahmin; 4 sınıfın (car, van, truck, bus) AP ortalaması. **ENGEL:** güven skoru sütunu, AP interpolasyonu (COCO 101 nokta mı VOC mu) ve tespit üst sınırı bilinmiyor → Kaggle Evaluation sayfası | BD s.3 |
| 3 | Submission formatı | **ENGEL — bilinmiyor.** Kutu koordinat düzeni (xyxy/xywh, piksel/normalize), sütunlar, tek satır/kutu mu → Kaggle `sample_submission` ve Evaluation sayfası | — |
| 4 | Günlük gönderim limiti | **5/gün**, gece yenilenir; Kaggle aşamasında toplam **10**. Finalde bunlardan **2**'si kullanılır. Yenilenme saati belgede "gece"; proje kuralı UTC gece yarısı (TR 03:00) varsayıyor — **doğrulanmadı** | BD s.3, SSS |
| 5 | İnternet / süre / GPU kısıtı | **ENGEL — bilinmiyor** → Kaggle Rules + notebook editörü | — |
| 6 | Veri boyutu ve dosyaları | Evren platformu COCO JSON dışa aktarımı (`Downloads/COCO_JSON`, `data/eda_split.py` ile ölçüldü, 25 Eyl): **6469 görüntü** (platform bölmesi 5823/646, birleştirildi), **165.332 kutu**, 290 boş görüntü; kategori id 0-3 = car/van/truck/bus. Kutu payı car %75,5 · van %13,8 · truck %7,3 · bus %3,4. Görüntü başı kutu ort 25,6, max 218. Çözünürlük karışık: 1400x1050 (2497), 1400x788, 2000x1500, 1360x765, 1916x1078, 1920x1080, 960x540. **Küçük nesne:** kutuların %38'i <32², 200 px² altı 0; 640'a küçültünce p5 kutu ≈ 7 px kenar. Bozuk kutu 0, çift etiket şüphesi 33, birebir kopya dosya 0, ardışık dosya numaralarında kutu benzerliği yok (sekans izi bulunmadı; yakın-kopya testi yapılmadı). **ENGEL:** bu verinin Kaggle train'i ile ilişkisi (aynısı mı, ek veri mi) ve test formatı bilinmiyor → Kaggle Data sayfası | BD s.3; EDA |
| 7 | Katılım ve kural kabulü yapıldı mı? | **ENGEL — bilinmiyor.** Tek ortak hesap kuralı: yalnız Coderspace'e bildirilen hesap katılabilir, birden fazla hesapla giriş/gönderim yasak (K-05 ile uyumlu). Kural kabulünü kimin yaptığı `STATUS.md`'de yok | BD s.3, SSS |
| 8 | Eşzamanlı koşu limiti | Ölçülmedi (paralel limit 2 varsayımı sürüyor) | — |
| 9 | Bitiş saati ve final seçim hakkı | Kaggle aşaması **iki gün** (insan teyidi; SSS "iki günlük" + 5/gün × 2 = 10 gönderimle tutarlı; s.3'teki "Cuma öğlenden Cumartesi öğlene" ifadesi bununla çelişiyor, geçerli sayılmıyor). Kesin bitiş saati **ENGEL** → Kaggle sayfası. Final seçimi: 10 gönderimden **2** | BD s.2, s.3, SSS; insan |
| 10 | Dış veri / hazır model izni; veriyi Kaggle dışına taşımak | **ENGEL — bilinmiyor.** Önceden eğitilmiş ağırlık (COCO/VisDrone vb.) ve dış veri izni belgede yok → Kaggle Rules. İzin çıkmadan pretrained ağırlıkla baseline yazılmaz | — |
| 11 | Kod teslimi / jüri kod değerlendirmesi; koşu yeri | **Var.** Final notebook Coderspace + ROKETSAN ile paylaşılacak (Aşama 1); Aşama 2 sonunda kod + sunum dosyası teslim, mentörlerle kod değerlendirme oturumu. Koşu yeri: Kaggle aşaması Kaggle üzerinden ilerliyor; yerel/Kaggle seçimi **ENGEL** (Rules'a bağlı) | BD s.2, s.3, s.4 |

## Görev
- Girdi → tahmin birimi → çıktı: drone görüntüsü → araç kutusu → (sınıf, kutu, güven?) — 4 sınıf: car, van, truck, bus. Yalnız alanı **≥ 200 px²** olan araçlar etiketli.
- Hedef değişken: kutu + sınıf (tablo hedefi değil). `kx.json` `target` doldurulamaz.
- ID kolonu: **ENGEL — bilinmiyor** (görüntü kimliği olması beklenir; doğrulanmadı).
- Grup / zaman kolonu: **ENGEL — bilinmiyor.** Aşama 2 metni 8 bölge ve 40 görüntüden söz ediyor; train/test'in bölge veya sahne bazlı ayrılıp ayrılmadığı veriye bakılarak öğrenilir. Ayrıysa fold gruplaması bölgeye/sahneye göre olmalı.

Kural notları (BD s.3): 200 px²'den küçük araçları veya yaya/bisikleti kutulamak **puanı etkilemez ama**
yaya, boş alan ve yanlış sınıf kutuları **yanlış tahmin** sayılır. Yani küçük araç kutusu serbest, sınıf/konum hatası ceza.
(Belge "puanı etkilemez" diyor; bunun uygulamada nasıl işlendiği — ignore bölgesi mi — doğrulanmadı.)

## Ürün bölümü (15 dk — Onay 1'i bekletmez)
- Kullanıcı kim: üs koruma görevlisi (BD s.3-4: "bir üssü korumakla görevlisiniz")
- Tahmin hangi kararı destekliyor: görüntüdeki araçların üs açısından risk oluşturup oluşturmadığı; durumun ne kadar kritik olduğu (Aşama 2 agent brief'i)
- Gerçek kullanımda hangi girdiler olacak: drone görüntüsü + harita bilgisi + araçların son 2 saatlik hareket kayıtları + serbest metin saha raporları. Çevre 8 bölge, günlük çıktı 40 görüntü
- Model nerede başarısız olur: belgeden doğrudan çıkan tek şey — saha raporlarının bir kısmı kasıtlı/yanlışlıkla hatalı veya konu dışı; agent raporlara değil kendi tespitine güvenmeli. Detektörün kendi başarısızlık noktaları veri görülmeden **bilinmiyor** (küçük/kısmi araç, van-car ve truck-bus karışıklığı bu aşamada hipotez, ölçülmedi)

> Dikkat: sadece yarışma dosyasının toplu istatistiklerinden türeyen feature'lar
> (global mean, target encoding vb.) yeni bir kullanıcı girdisinde nasıl üretilecek?
> KABUL anında `card.md`'ye tek satır not düşülür.

## Jüri / değerlendirme
- Kaggle skoru dışındaki kriterler (BD SSS): problemin önemi ve iş değeri · çalışan ürün ortaya koyabilme · ürün düşüncesi ve kullanıcı deneyimi · sunum ve demo · mentörler: Aşama 2 teknik kalite ve mimari (kod değerlendirme oturumu)
- Ağırlıkları: **belgede yok** ("belli bir yüzde" deniyor; Private Leaderboard skoru final sunum puanına doğrudan ekleniyor). Sayı yok → mentörden/organizasyondan sorulacak
- İkinci aşamada beklenen çıktı: 4 adımlı LLM agent — (1) araçları tespit et, (2) piksel → gerçek koordinat (harita bilgisiyle), (3) hareket verisiyle son 2 saatin hız/yön/rota çıkarımı, (4) saha raporlarıyla birlikte risk analizi → kısa brief. Kod + final sunum dosyası teslim; canlı demo (chatbot/web/CLI/sesli), agent en az 1-2 verilen görüntüde gerçekten çalışmalı
- Kaggle sıralaması kötü olan ekip elenmez (SSS)

## Açık sorular / engeller
- **Proje altyapısı tablo varsayıyor.** `tools/make_folds.py --target`, `core/metric.py` (ROC AUC şablonu), `blend.py` (tek tahmin kolonu, `oof.parquet`) ve `kx.json` `target` görüntü tespitine uymuyor. Fold görüntü (ve varsa bölge) bazında kurulmalı; `core/metric.py` mAP@0.5 olmalı; ensemble tespit için kutu birleştirme (WBF vb.) ister, `blend.py --rank` işe yaramaz. **Karar (insan): altyapı tamamen case'e göre yeniden kurulacak; Kaggle dosyaları paylaşıldıktan sonra.**
- Belgede olmayan, Kaggle sayfasından gelmesi gerekenler: submission formatı, veri/etiket formatı, çözünürlük, dış veri/pretrained izni, GPU/süre limiti, kesin bitiş saati, code competition mı.
- Aşama 2'de Kaggle'daki Aşama 1 modeli kullanılacak (insan teyidi) — model dışa aktarılabilir/taşınabilir olmalı; taşıma izni Rules'a bağlı (satır 10).
- Puan ağırlıkları (Private LB / mentör / jüri) yok.
- Aşama 2'nin "harita bilgisi" ve "hareket kayıtları" veri formatı henüz paylaşılmadı (belge: "sizinle paylaşılacak"). Piksel→koordinat dönüşümü bu bilgiye bağlı; Aşama 1 modeli bunun için kutu merkezini koruyacak çıktı vermeli (hipotez, ölçülmedi).
