# tools/ — otomasyon

**Aşama:** 2'den sonuna kadar. **Hiçbiri Kaggle'a gönderim yapmaz.**

| Dosya | Ne işe yarar |
|---|---|
| `kx.py` | `new` (deney klasörü + koşulacak `code.py`) · `kayit` (yerel çıktıyı DOĞRULA + kaydet) · `cmp` (parent ile fold fold karşılaştır, gürültü tabanıyla) · `gurultu` (özdeş koşudan `noise_floor`) · `board` (tek ekran) |
| `code_template.py` | Tek hücrelik iskelet; Kaggle'da ve yerelde değişmeden koşar. Fold ve metrik blokları `core/`'dan aynen gömülür; deneyden deneye yalnız `TEKNIKLER`, `hazirla`, `fold_hazirla`, `model_kur`, `egit`, `tahmin` değişir (kurallar: `SOZLESME.md`) |
| `make_folds.py` | D-01'den sonra bir kez: `core/folds.csv` + fold parmak izi üretir (`--group` / `--time`) |
| `adv_val.py` | Yerel adversarial validation: train-vs-test AUC + en çok kayan kolonlar (D-01 kanıtı) |
| `blend.py` | OOF'lardan ensemble ağırlığı; `--rank` AUC/AP için sıra ortalaması |
| `test_kx.py` | Doğrulayıcı testleri (45 senaryo). `python tools/test_kx.py` — geçici klasörde mini repo kurar, gerçek repoya dokunmaz |

**Kim çalıştırır:** ajan. Koşuyu insan Kaggle'da yapar; bu araçlar yalnız yerelde
üretir, doğrular ve karşılaştırır.

**Değiştirirken:** `kx.py` Kaggle CLI'yi çağırmaz. Bu bir üslup tercihi değil, karar —
`grep -n "kernels push" tools/` boş dönmelidir.
