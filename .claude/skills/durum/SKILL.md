---
name: durum
description: Durum turu ve vardiya devri - T+saat, Kaggle'da ne koşuyor, kalan süre ve gönderim hakkı, son FULL başlatma saati, kapsam riski ve sıradaki 3 iş. Kullanım - /durum ya da /durum devir
disable-model-invocation: true
argument-hint: "[devir]"
---

# Durum turu

2-3 saatte bir ve gece nöbetinde çalıştır. Amaç: zamanı ve gönderim hakkını görünür
kılmak, kapsam riskini erken yakalamak. **Sen resmi çizersin, kararı insan verir.**

## Tur

1. **Bak — sormadan önce.**
   - `python tools/kx.py board` — koşanlar, son sonuçlar, mevcut en iyi aday
   - `STATUS.md` son kontrol saati · `case/CASE.md` takvim ve limitler
   - `log/SUBMISSIONS.md` kalan hak · `log/MENTOR.md` sonucu yazılmamış aksiyonlar
   - `log/BACKLOG.md` ŞİMDİ kovasında kaç madde kaldı
   - Kaggle salt okunur: `kaggle competitions submissions <slug>`
   Tamam: her kaynağın sonucu ya da "yok".

2. **Hesapla.**
   - T+saat ve **bitişe kalan süre**
   - **Son FULL başlatma saati = bitiş − (ölçülen koşu süresi × 1.5) − 45 dk.**
     Bu saat `STATUS.md`'ye yazılır ve geçilmez.
   - Gönderim hakkının yenilenmesine kalan süre (UTC gece yarısı = TR 03:00)
   - Kalan GPU kotası (bilinmiyorsa "bilinmiyor" yaz, tahmin etme)

3. **Kapsam kontrolü.** Süren işler kalan süreye sığıyor mu? Sığmıyorsa **kesilecek
   veya ertelenecek en küçük şeyi tek öneri olarak** yaz, gerekçesiyle.
   Kapanış rezervini kalan süreden düş; sığmayan deneyi önerme.
   ŞİMDİ kovasında 3'ten az madde kaldıysa `CODEX.md` Çağrı 4'ü tetikle.

4. **Yaz.** `STATUS.md`'yi yeniden yaz (≤60 satır, en üst satır "insandan sıradaki
   eylem"). Çürüme kuralı `CLAUDE.md` kural 8'de. Ayrıca panoya yapıştırılabilir
   kısa sürümü ver:

       ## Durum T+<saat> (<gün saat>)
       - Kaggle'da koşan: <slug> - tahmini bitiş <..>
       - Biten: <EXP - karar - skor>
       - Ana hat: <EXP> (<ana skor>)
       - Skor: en iyi yerel <..> · LB <..> · kalan hak <n> (yenilenme <saat>)
       - Son FULL başlatma saati: <..>  |  Kalan GPU kotası: <..>
       - Kapsam: yetişiyor | risk: <ne> -> öneri: <kes/ertele>
       - Mentor: açık aksiyon <n> (en eskisi: <..>)
       - Sıradaki 3 iş: 1. <..> 2. <..> 3. <..>

   Tamam: `STATUS.md` güncel, kısa sürüm kullanıcıda.

## `/durum devir`

Nöbeti devrederken tura ek olarak 5 satır üretilir. Bu satırlar panoya
verilmekle kalmaz, `STATUS.md`'ye kalıcı olarak yazılır:
- "Ne yapıldı" + "Çalışır durumda mı" → `Bu oturumda ne oldu`
- "Nerede kaldı" + "Dikkat" → `Nerede kaldım / dikkat`
- "Sıradaki adım" → `İnsandan sıradaki eylem`

Panoya yapıştırılabilir kısa sürüm:

- Ne yapıldı: <EXP'ler, kararlar>
- Nerede kaldı: <yarım deney, bekleyen koşu>
- Çalışır durumda mı: <son doğrulanan çıktı ve saati>
- Sıradaki adım: <tek adım>
- Dikkat: <tuzak, yarım kalan karar, geçilmemesi gereken saat>

## Sınırlar

- Gerçek takip yoksa "izliyorum" deme; **son kontrol saatini yaz.**
- Gönderim sayısını deney sayısından türetme; resmi kaynaktan oku.
- Yalnız aynı ölçüm sözleşmesindeki tamamlanmış FULL koşuları karşılaştır;
  FAST ve "koşmadı" kayıtlarını ayrı göster.
- Ağ sorgusu başarısızsa son yerel kaydı saati ile göster, güncelmiş gibi sunma.
