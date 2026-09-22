---
name: mentor
description: Mentor ve jüri geri bildirimini kaydeder, somut aksiyona çevirir, açık soruları kuyruğa yazar ve görüşme öncesi "şunu dediniz, şunu yaptık, sonuç bu" tablosunu üretir. Kullan - mentor bir öneri/eleştiri/soru ilettiğinde, bir mentor aksiyonu bittiğinde, mentor veya jüri görüşmesinden önce.
---

# Mentor notu

Dosya: `log/MENTOR.md`. **Yalnız sona ekleme.** Bir kaydın sonucu, eski kaydı
değiştirerek değil, onu anan yeni bir kayıtla yazılır.

Mentorlar geri bildirime verilen cevabı ve ne kadar uygulandığını takip ediyor.
Görevin her geri bildirimi önce somut bir aksiyona, sonra kanıta bağlamak.

## Mod 1 — Mentor bir şey söyledi

1. **Söyleneni mentorun kelimelerine yakın yaz.** Birebirse tırnak içinde, özetse
   "özet:" diye. Kendi yorumunla karıştırma.
2. **Etkisini bul.** Hangi dosya, karar, metrik veya demo adımı etkileniyor?
3. **Takımın tutumunu yaz:** katılıyoruz | kısmen | katılmıyoruz + tek cümle gerekçe.
   Katılmıyorsak bunu mentora nasıl anlatacağımızı da yaz — **bu da bir cevaptır.**
4. **Aksiyonu tek somut adıma indir:** ne, ne zamana kadar.
5. **Anlaşılmayan her noktayı "Sorulacak" kuyruğuna yaz.** Mentorun söylediğinin
   dayanağı, kapsamı veya nasıl uygulanacağı belirsizse soru üret. Belirsizliği
   "anladım" diye geçiştirme — sonraki görüşmede sorulacak liste budur.
6. `log/MENTOR.md` sonuna ekle:

       ### Mentor - <gün saat> - <mentor adı/alanı>
       - Söylenen: "<alıntı>" | özet: <..>
       - Etki: <dosya/karar/metrik>
       - Tutum: katılıyoruz | kısmen | katılmıyoruz - <gerekçe>
       - Aksiyon: <adım> · <saat>
       - Sorulacak: <anlaşılmayan nokta> | yok

   Sorulacak varsa dosyanın üstündeki **"Açık sorular"** tablosuna da satır ekle.

Tamam: kayıt eklendi, aksiyonun saati var, açık sorular tabloya düştü.

## Mod 2 — Aksiyon bitti

`log/MENTOR.md` sonuna ekle:

    ### Mentor sonucu - <gün saat> - (<ilk kaydın başlığı>)
    - Ne yaptık: <..>
    - Kanıt: <EXP no, skor farkı, komut çıktısı, dosya yolu>

**Kanıt yoksa kaydı yazma** — önce kanıtı üret (ölçümü çalıştır, deneyi bitir).
Olumsuz veya belirsiz sonuç da mentor geri bildirimine verilmiş bir cevaptır;
başarılıymış gibi yazma.

## Mod 3 — Görüşmeden önce

Bütün kayıtları ve sonuçları oku, iki çıktı ver:

| Mentor ne dedi | Ne yaptık | Kanıt | Açık kalan ve nedeni |
|---|---|---|---|

Sonucu olmayan her kaydı **"açık"** diye işaretle.

Altına görüşmeyi açacak 2-3 cümle:
"Geçen sefer <..> dediniz; <..> yaptık; sonuç <..>. <Açık kalan> için planımız <..>."

Sonra **"Açık sorular"** tablosunu önüne koy — bu görüşmede sorulacaklar listesi budur.
En eski soru en üstte. Cevaplanan soru silinmez, "→ cevap:" ile tamamlanır.

## Deneyle bağlantı

Skoru etkileyen mentor önerisi `log/BACKLOG.md` kuyruğuna hipotez olarak bağlanır.
Kanıt `experiments/EXP-xxx/card.md`'deki KABUL/HAVUZ/RED kararına bağlanır.
**Mentor önerisi ölçülmeden "yapıldı" sayılmaz.**

"Mentor önerdi" bir dayanak değil, öneren kişidir (`log/BACKLOG.md` kuralı).
Dayanak, bu veride ölçülmüş gözlemdir.
