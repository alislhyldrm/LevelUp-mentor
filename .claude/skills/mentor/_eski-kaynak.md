---
name: mentor-notu
description: Mentor geri bildirimini kaydeder, aksiyona çevirir ve izler; docs/NOTLAR.md'ye Mentor kayıtları. Kullan - mentor bir öneri, eleştiri ya da soru ilettiğinde; bir mentor aksiyonu bittiğinde; mentor ya da jüri görüşmesinden önce geçmiş geri bildirimlerin özeti istendiğinde.
---

# Mentor notu

Mentorlar ve İK, geri bildirime verilen cevabı ve ne kadar uygulandığını takım üyeleri bazında gözlemliyor (`Digital-mentor/meeting.md`). Görevin, her geri bildirimi somut bir aksiyona ve sonra kanıta bağlamak; böylece sonraki görüşmede takım "şunu dediniz, şunu yaptık, sonuç bu" diyebilir.

`docs/NOTLAR.md` yalnız sona ekleme alır. Bir kaydın sonucu, eski kaydı değiştirerek değil, onu anan yeni bir kayıtla yazılır.

## Kayıt: mentor bir şey söyledi

1. Söyleneni mentorun kelimelerine yakın yaz. Birebir alıntıysa tırnak içinde, özetse "özet:" diye.
2. Etkisini bul: hangi dosya, karar, metrik ya da demo adımı etkileniyor? Takımın tutumu: katılıyoruz | kısmen | katılmıyoruz, tek cümle gerekçe. Katılmıyorsak mentora bunu nasıl anlatacağımızı yaz; bu da bir cevaptır.
3. Aksiyonu tek somut adıma indir: ne, kim, ne zamana kadar.
4. `docs/NOTLAR.md` sonuna ekle:

   ```markdown
   ### Mentor — <gün saat> — <mentor adı ya da alanı>
   - Söylenen: "<alıntı>" | özet: <..>
   - Etki: <dosya/karar/metrik>
   - Tutum: katılıyoruz | kısmen | katılmıyoruz — <gerekçe>
   - Aksiyon: <adım> · sahip: <kişi> · <saat>
   ```
   Tamam: kayıt eklendi; aksiyonun sahibi ve saati var.

## Sonuç: aksiyon bitti

`docs/NOTLAR.md` sonuna ekle:

```markdown
### Mentor sonucu — <gün saat> — (<ilk kaydın başlığı>)
- Ne yaptık: <..>
- Kanıt: <commit, skor farkı, ekran/komut çıktısı>
```

Kanıt yoksa kaydı yazma; önce kanıtı üret (testi ya da ölçümü çalıştır).

## Özet: görüşmeden önce

Bütün Mentor kayıtlarını ve sonuçlarını oku, kullanıcıya şu tabloyu ver:

| Mentor ne dedi | Ne yaptık | Kanıt | Açık kalan ve nedeni |
|---|---|---|---|

Altına görüşmeyi açacak 2-3 cümle yaz: "Geçen sefer <..> dediniz; <..> yaptık; sonuç <..>. <Açık kalan> için planımız <..>." Sonucu olmayan her kaydı "açık" diye işaretle.

## Deneyle bağlantı

Skoru etkileyen mentor önerisini `docs/DENEYLER.md` kuyruğuna hipotez olarak bağla; onaylı kapsam içindeyse rutin deney için tekrar başlangıç onayı isteme. Kanıt `runs/<id>/result.json` ve tut/ele/tekrar ölç kararına bağlanır. Olumsuz veya belirsiz sonuç da mentor geri bildirimine verilmiş bir cevaptır; başarılıymış gibi yazma.
