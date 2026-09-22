# tools/ — otomasyon

**Aşama:** 2'den sonuna kadar. **Hiçbiri Kaggle'a gönderim yapmaz.**

| Dosya | Ne işe yarar |
|---|---|
| `kx.py` | `new` (deney klasörü + koşulacak `code.py`) · `kayit` (yerel çıktıyı DOĞRULA + kaydet) · `cmp` (parent ile fold fold karşılaştır) · `board` (tek ekran) |
| `code_template.py` | Kaggle'a yapıştırılan tek hücrelik iskelet. Fold ve metrik blokları `core/`'dan aynen gömülür; deneyden deneye yalnız `hazirla()` ve `model_kur()` değişir |
| `make_folds.py` | D-01'den sonra bir kez: `core/folds.csv` + fold parmak izi üretir |
| `blend.py` | OOF'lardan ensemble ağırlığı |
| `test_kx.py` | Doğrulayıcı testleri (21 senaryo). `python tools/test_kx.py` — geçici klasörde mini repo kurar, gerçek repoya dokunmaz |

**Kim çalıştırır:** ajan. Koşuyu insan Kaggle'da yapar; bu araçlar yalnız yerelde
üretir, doğrular ve karşılaştırır.

**Değiştirirken:** `kx.py` Kaggle CLI'yi çağırmaz. Bu bir üslup tercihi değil, karar —
`grep -n "kernels push" tools/` boş dönmelidir.
