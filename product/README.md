# product/ — ikinci aşama köprüsü (jüri / ürün)

**Aşama:** 4, skor işi oturduktan sonra. **Şu an boş.**

**Neden var:** model yalnız puana göre kurulmaz. Jüri "bu gerçek hayatta nasıl
çalışır" diye sorduğunda cevabın kodu burada olur.

**Dolacak içerik:**
- `predict.py` — tek bir JSON/satır girdi alıp tahmin döndüren **tek giriş noktası**.
- Eğitilmiş ağırlıklar + ön işleme nesneleri + kolon/sınıf sırası + paket sürümleri.

**Tamamlanma ölçütü:** "model kaydedildi" değil — **"temiz bir oturumda yüklenip tekrar
tahmin üretti"**. Sürüm uyuşmazlığı riski için bu test modelin eğitildiği ortamda
(veya eşleşen sürümlerle) yapılır.

**Dikkat:** yalnız yarışma dosyasının toplu istatistiğinden türeyen feature'lar (global
mean, target encoding) gerçek bir kullanıcı girdisinde nasıl üretilecek? KABUL anında
`card.md`'ye tek satır not düşülür; cevabı olmayan feature burada sorun çıkarır.
