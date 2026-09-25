# bilgilendirme-dokumani.pdf (levelup.roketsan.com.tr) — ham kayıt

Kaynak: insanın telefonda çektiği ekran görüntüleri (saat 14:48, 25 Eyl 2026). Resmi PDF, 2,4 MB.
Metin **özetlenmeden** yazıldı; ekran görüntüsünden elle aktarıldı, olası harf hatası olabilir.
**Görülmeyen sayfalar: 1/5 ve 5/5.** Aşağıdaki bölümler ekranda göründüğü sırayla.
Bu dosya değiştirilmez; yeni sürüm yeni dosyadır.

---

## Sayfa 2 / 5

Merhaba sevgili Level Up AI | ROKETSAN Yapay Zekâ Hackathonu katılımcıları,

25 Eylül Cuma başlayacak ve 27 Eylül Pazar'a kadar sürecek bu yarışmada sizden **iki aşamalı bir çalışma** beklenmektedir.
İlk aşamada, fotoğraflardaki araçları tespit eden ve otomobil, minibüs, kamyon veya otobüs olarak sınıflandıran bir **yapay zekâ modeli geliştirmeniz beklenmektedir**. Kaggle üstünden ilerleyecek bu ilk aşamada modellerinizi iyileştirerek sıralamada üst sıralara çıkmak için yarışacaksınız.

İkinci aşamada, fotoğraflardaki araçlara ait hareket kayıtları ve sahadan gelen ihbarlar sizinle paylaşılacak. Takım olarak, verilen bir fotoğrafı bu verilerle birlikte değerlendirerek görüntüdeki durumun ne kadar kritik olduğuna karar veren ve kararını gerekçelendiren bir **yapay zekâ ajanı geliştirmeniz** beklenmektedir.

---

## Sayfa 3 / 5

### AŞAMA 1: ARAÇ TESPİTİ (KAGGLE)

Drone görüntülerinde alanı 200 px² veya daha büyük araçları **tespit edip** dört sınıftan (car, van, truck, bus) birine yerleştiren bir model geliştireceksiniz.

Eğitim görüntülerindeki araçların konumu ve sınıfı Kaggle içerisindeki datalarda size verilmiş durumda.

Test görüntülerindekileri modelinizle siz tespit edeceksiniz. 200 px²'den küçük araçlar ile yaya ve bisiklet gibi başka nesneler ne train ne de test setinde etiketlenmemiştir. Böyle bir aracı işaretlemeniz puanınızı etkilemez ama yaya, boş alan ya da yanlış sınıf için çizdiğiniz kutu yanlış tahmin sayılır.

Değerlendirme mAP@0.5 metriğiyle yapılıyor: bir tahmin, sınıfı doğruysa ve tahmin kutusuyla gerçek kutu arasındaki IoU en az 0.5 ise doğru sayılıyor; dört sınıfın AP değerinin ortalaması skorunu oluşturuyor.

Bu aşamada kullanmanız beklenen ilgili dosyalara **Kaggle'daki yarışma içerisinden ulaşabileceksiniz**.

**KAGGLE KATILIM KURALLARI**

Her takım yalnızca Coderspace'e daha önce bildirilen tek bir hesapla yarışmaya katılabilir; birden fazla hesapla giriş ya da gönderim yapılamaz. Günlük submission sınırı 5 ve sınır gece yenilenecektir; Cuma öğlenden Cumartesi öğlene kadar süren Kaggle aşamasında takım başına toplam 10 gönderim hakkınız olacaktır. Oluşturduğunuz final notebook'u Coderspace ve ROKETSAN ekipleriyle paylaşmanız beklenecektir.

**PUANLAMA**

Yarışma bitince oluşacak Private Leaderboard skorunuz, final sunum puanınıza doğrudan eklenecektir.

---

## Sayfa 3 / 5 (devam) — AŞAMA 2 başlangıcı

### AŞAMA 2: SAHA RAPORU DESTEKLİ LLM AGENT

Senaryoda bir üssü korumakla görevlisiniz. Çevredeki 8 bölge gün boyu drone'larla izlenmektedir ve sahadaki birimlerden de gözlem raporları gelmektedir. Elinizde bu izlemenin bir günlük çıktısı bulunur: 40 drone görüntüsü, araçların son iki saatlik hareket kayıtları ve serbest metin saha raporları.

Bu aşamada, birinci gün geliştirdiğiniz tespit modelini kullanan bir LLM agent oluşturmanız beklenmektedir. Agent, kendisine verilen bir görseldeki araçları analiz ederek bu araçların üs açısından risk oluşturup [oluşturmadığını...] (satır ekran görüntüsünde kesik; tam hali sayfa 4'te)

---

## SIKÇA SORULAN SORULAR (sayfa numarası ekran görüntüsünde görünmüyor; 3/5 ile 4/5 arasında)

(önceki sayfadan kesik satırlar:) mentörlerden alacağınız puan final puanınızda belli bir yüzdeyi oluşturacaktır. Ardından jürilere sunumunuzla çalışmanızı aktarmanız beklenecektir.

Sunum içerisinde projenizin çalışılabilirliğini agent'ı bir chatbot arayüzü, bir web uygulaması, komut satırı ya da sesli asistan olarak canlı gösterebilirsiniz. Agent'ınızın verilen görüntülerden en az bir ya da iki tanesi üzerinde gerçekten çalıştığını görebilmemiz önemlidir.

**Kaggle'a birden fazla hesapla katılabilir miyiz?**
Hayır, takım başına sadece Coderspace'e bildirilen tek hesap geçerli.

**Günde kaç gönderim hakkımız var?**
Günlük submission sınırınız 5'tir. Bu sınır gece yenilenecektir. İki günlük Kaggle aşamasında toplam 10 submission hakkınız olacaktır. Finalde bunlardan 2'sini kullanabileceksiniz.

**Aşama 1'deki skorumuz düşükse Aşama 2'de dezavantajlı mı oluruz?**
Private Leaderboard skorunuz final puanınızın belirli bir yüzdeliğini oluşturacaktır. Bu yüzden Kaggle aşamasında başarı göstermeniz sizin için faydalı olacaktır. Kaggle aşamasında sıralaması kötü ekipler elenmeyecektir.

(vurgulu kutu:) İkinci aşamadaki teknik kalite ve mimariniz mentörler tarafından değerlendirilecek, ayrıca final sunumlarında jüriler problemin önemi ve iş değeri, çalışan ürün ortaya koyabilme, ürün düşüncesi ve kullanıcı deneyimi, sunum ve demo başlıkları üzerinden de sizi değerlendirerek final puanınızı belirleyecektir.

ROKETSAN İNSAN KAYNAKLARI

---

## Sayfa 4 / 5

### AŞAMA 2: SAHA RAPORU DESTEKLİ LLM AGENT

Senaryoda bir üssü korumakla görevlisiniz. Çevredeki 8 bölge gün boyu drone'larla izlenmektedir ve sahadaki birimlerden de gözlem raporları gelmektedir. Elinizde bu izlemenin bir günlük çıktısı bulunur: 40 drone görüntüsü, araçların son iki saatlik hareket kayıtları ve serbest metin saha raporları.

Bu aşamada, birinci gün geliştirdiğiniz tespit modelini kullanan bir LLM agent oluşturmanız beklenmektedir. Agent, kendisine verilen bir görseldeki araçları analiz ederek bu araçların üs açısından risk oluşturup oluşturmadığını açıklayan kısa bir brief üretecektir. Bunun için agent'ın aşağıdaki adımları yerine getirmesi gerekmektedir:

1. Görseldeki araçları doğru biçimde tespit etmek,
2. Piksel konumlarını harita bilgisiyle gerçek koordinatlara çevirmek,
3. Bu koordinatları hareket verisiyle eşleştirerek araçların son iki saat içindeki hızını, yönünü ve rotasını çıkarmak,
4. Tüm bu bulguları saha raporlarıyla birlikte değerlendirerek risk analizi yapmak.

(uyarı kutusu:) Saha raporlarının tamamı doğru değildir; bazıları kasıtlı ya da yanlışlıkla hatalı, bazıları ise konuyla ilgisiz olabilir. Bu nedenle agent'ınızın raporları olduğu gibi kabul etmek yerine kendi tespitine güvenmesi beklenmektedir.

Bu aşama sonunda sizden kodlarınızı ve final sunum dosyanızı paylaşmanızı isteyeceğiz. Kodlarınız mentörlerle kod değerlendirme oturumunuzda değerlendirilecektir. Teknik kalite ve mimari incelenerek mentörlerden alacağınız puan final puanınızda belli bir yüzdeyi oluşturacaktır. Ardından jürilere sunumunuzla çalışmanızı aktarmanız beklenecektir.

Sunum içerisinde projenizin çalışılabilirliğini agent'ı bir chatbot arayüzü, bir web uygulaması, komut satırı ya da sesli asistan olarak canlı gösterebilirsiniz. Agent'ınızın verilen görüntülerden en az bir ya da iki tanesi üzerinde gerçekten çalıştığını görebilmemiz önemlidir.
