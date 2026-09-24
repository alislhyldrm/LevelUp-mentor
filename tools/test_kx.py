"""kx.py dogrulayici testleri - gercek repoya DOKUNMAZ.

Calistir: python tools/test_kx.py

Scratchpad'de mini bir repo kurar, tools/kx.py'yi oraya kopyalar ve
validate_output'u sentetik senaryolarla sinar.
"""
import json
import shutil
import tempfile
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REAL = Path(__file__).resolve().parent.parent
SCRATCH = Path(tempfile.gettempdir()) / "kx_test_minirepo"

gecti, kaldi = [], []


def kontrol(ad, sart, detay=""):
    (gecti if sart else kaldi).append(ad)
    print(f"  {'GECTI ' if sart else 'KALDI '} {ad}" + (f"   {detay}" if detay and not sart else ""))


def kur():
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    for d in ("tools", "core", "data", "experiments", "log"):
        (SCRATCH / d).mkdir(parents=True)
    for f in ("tools/kx.py", "tools/code_template.py", "tools/make_folds.py",
              "tools/blend.py", "tools/adv_val.py",
              "core/folds_snippet.py", "core/metric.py"):
        shutil.copy(REAL / f, SCRATCH / f)
    (SCRATCH / "kx.json").write_text(json.dumps({
        "initials": "as", "competition": "test", "target": "y_ham", "id_col": "id",
        "pos_label": "Yes", "sample_submission": "data/sample_submission.csv",
        "main_score": "cv_oof", "greater_is_better": True,
    }, indent=2), encoding="utf-8")

    # kucuk sentetik veri
    n, m = 400, 120
    rng = np.random.RandomState(7)
    train = pd.DataFrame({
        "id": np.arange(n),
        "a": rng.rand(n),
        "b": rng.randint(0, 5, n),
        "y_ham": np.where(rng.rand(n) < 0.3, "Yes", "No"),
    })
    train["grp"] = rng.randint(0, 40, n)
    train["t"] = rng.randint(0, 25, n)
    train.to_csv(SCRATCH / "data" / "train.csv", index=False)
    pd.DataFrame({
        "id": np.arange(1000, 1000 + m), "a": rng.rand(m), "b": rng.randint(0, 5, m),
        "grp": rng.randint(40, 60, m), "t": rng.randint(25, 30, m),
    }).to_csv(SCRATCH / "data" / "test.csv", index=False)
    pd.DataFrame({"id": np.arange(1000, 1000 + m), "y_ham": 0.5}).to_csv(
        SCRATCH / "data" / "sample_submission.csv", index=False)


def kx(*args):
    return subprocess.run([sys.executable, str(SCRATCH / "tools" / "kx.py"), *args],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def gecerli_submission():
    return pd.read_csv(SCRATCH / "data" / "sample_submission.csv").copy()


def deney_kur(exp, result, sub=None):
    d = SCRATCH / "experiments" / exp / "output"
    if d.parent.exists():
        shutil.rmtree(d.parent)
    d.mkdir(parents=True)
    (d / "result.json").write_text(json.dumps(result), encoding="utf-8")
    if sub is not None:
        sub.to_csv(d / "submission.csv", index=False)
    return d


def main():
    kur()
    print("\n--- 1) make_folds.py ---")
    r = subprocess.run([sys.executable, str(SCRATCH / "tools" / "make_folds.py"),
                        "--target", "y_ham", "--pos", "Yes"],
                       capture_output=True, text=True, cwd=SCRATCH, encoding="utf-8")
    kontrol("folds.csv uretildi", (SCRATCH / "core" / "folds.csv").exists(), r.stderr)
    fp = ""
    for line in r.stdout.splitlines():
        if "FOLD PARMAK IZI" in line:
            fp = line.split(":")[-1].strip()
    kontrol("parmak izi basildi", len(fp) == 12, repr(fp))

    r2 = subprocess.run([sys.executable, str(SCRATCH / "tools" / "make_folds.py"),
                         "--target", "y_ham", "--pos", "Yes"],
                        capture_output=True, text=True, cwd=SCRATCH, encoding="utf-8")
    kontrol("ikinci kez uretim ENGELLENDI (fold'lar sabit)", r2.returncode != 0)

    temel = {"exp_id": "EXP-001", "parent": "-", "owner": "claude", "mode": "FULL",
             "seed": 42, "fold_scores": [0.9, 0.91, 0.89, 0.9, 0.905],
             "cv_mean": 0.901, "cv_oof": 0.9, "n_folds_done": 5, "n_rows_oof": 400,
             "fold_fingerprint": fp, "runtime_min": 1.0, "note": "test"}

    print("\n--- 2) fold parmak izi ---")
    deney_kur("EXP-001", temel, gecerli_submission())
    out = kx("kayit", "EXP-001")
    kontrol("dogru parmak izi -> GECTI", "DOGRULAMA GECTI" in out.stdout, out.stdout + out.stderr)

    bozuk = dict(temel, fold_fingerprint="ffffffffffff")
    deney_kur("EXP-002", dict(bozuk, exp_id="EXP-002"), gecerli_submission())
    out = kx("kayit", "EXP-002")
    kontrol("bozuk parmak izi -> KAYDA GIRMEDI",
            out.returncode != 0 and "PARMAK IZI TUTMUYOR" in out.stdout, out.stdout)

    eksik = {k: v for k, v in temel.items() if k != "fold_fingerprint"}
    deney_kur("EXP-003", dict(eksik, exp_id="EXP-003"), gecerli_submission())
    out = kx("kayit", "EXP-003")
    kontrol("parmak izi yok -> KAYDA GIRMEDI",
            out.returncode != 0 and "fold_fingerprint" in out.stdout, out.stdout)

    print("\n--- 3) submission format kontrolu ---")
    senaryolar = []

    s = gecerli_submission(); s.columns = ["id", "yanlis_ad"]
    senaryolar.append(("kolon adi yanlis", s, "kolonlari"))

    s = gecerli_submission().iloc[:-3]
    senaryolar.append(("satir eksik", s, "satir"))

    s = gecerli_submission().sample(frac=1.0, random_state=1).reset_index(drop=True)
    senaryolar.append(("id sirasi karisik", s, "SIRA farkli"))

    s = gecerli_submission(); s.loc[0, "y_ham"] = np.nan
    senaryolar.append(("NaN var", s, "NaN"))

    s = gecerli_submission(); s.loc[0, "id"] = 999999
    senaryolar.append(("id kumesi tutmuyor", s, "id kumesi tutmuyor"))

    for i, (ad, sub, beklenen) in enumerate(senaryolar, start=10):
        exp = f"EXP-0{i}"
        deney_kur(exp, dict(temel, exp_id=exp), sub)
        out = kx("kayit", exp)
        kontrol(f"submission: {ad} -> yakalandi",
                out.returncode != 0 and beklenen in out.stdout, out.stdout)

    print("\n--- 4) referans dosya yoksa bloklamaz ---")
    ref = SCRATCH / "data" / "sample_submission.csv"
    yedek = ref.read_bytes()
    ref.unlink()
    deney_kur("EXP-020", dict(temel, exp_id="EXP-020"), gecerli_submission_yok := None)
    out = kx("kayit", "EXP-020")
    kontrol("referans yok -> GECTI + uyari",
            out.returncode == 0 and "ATLANAN DOGRULAMA" in out.stdout, out.stdout)
    ref.write_bytes(yedek)

    print("\n--- 5) run_log.txt'den result.json uretimi ---")
    d = SCRATCH / "experiments" / "EXP-030" / "output"
    if d.parent.exists():
        shutil.rmtree(d.parent)
    d.mkdir(parents=True)
    log = ("fold 0: 0.9\nbir suru cikti\n"
           "=== KX RESULT JSON ===\n" + json.dumps(dict(temel, exp_id="EXP-030")) +
           "\n=== KX RESULT SONU ===\n")
    (d / "run_log.txt").write_text(log, encoding="utf-8")
    gecerli_submission().to_csv(d / "submission.csv", index=False)
    out = kx("kayit", "EXP-030")
    kontrol("ekran ciktisindan result.json uretildi",
            out.returncode == 0 and (d / "result.json").exists(), out.stdout)

    d2 = SCRATCH / "experiments" / "EXP-031" / "output"
    d2.mkdir(parents=True)
    (d2 / "run_log.txt").write_text("sadece rastgele cikti, blok yok\n", encoding="utf-8")
    out = kx("kayit", "EXP-031")
    kontrol("bloksuz log -> anlasilir hata",
            out.returncode != 0 and "KX RESULT JSON" in (out.stdout + out.stderr), out.stderr)

    print("\n--- 6) new + board ---")
    out = kx("new", "EXP-040", "--note", "test deneyi", "--target", "y_ham", "--pos-label", "Yes")
    d = SCRATCH / "experiments" / "EXP-040"
    kontrol("new: code.py + card.md + diff.md uretildi",
            all((d / f).exists() for f in ("code.py", "card.md", "diff.md")), out.stdout + out.stderr)
    if (d / "code.py").exists():
        kod = (d / "code.py").read_text(encoding="utf-8")
        import ast
        try:
            ast.parse(kod)
            syn = True
        except SyntaxError as e:
            syn, out.stdout = False, str(e)
        kontrol("uretilen code.py syntax temiz", syn, out.stdout)
        kontrol("fold snippet gomuldu", "def fold_fingerprint" in kod and "def make_folds" in kod)
        kontrol("metrik gomuldu", "GREATER_IS_BETTER" in kod)
        kontrol("yer tutucu kalmadi", all("__" + t + "__" not in kod for t in (
            "FOLD_SNIPPET", "TARGET", "GROUP_COL", "TIME_COL", "OWNER", "SLUG")))

    out = kx("board")
    kontrol("board Kaggle cagirmadan calisti", out.returncode == 0, out.stderr)
    kontrol("board yerel parmak izini gosteriyor", fp in out.stdout, out.stdout)

    print("\n--- 7) takim kimligi (kx.json owners) ---")
    cfg_yol = SCRATCH / "kx.json"
    cfg = json.loads(cfg_yol.read_text(encoding="utf-8"))
    cfg["owners"] = {"3": "ay"}
    cfg_yol.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    out = kx("new", "EXP-301", "--note", "takim deneyi", "--target", "y_ham", "--pos-label", "Yes")
    kontrol("owners: EXP-301 -> owner=ay, ay-exp-301",
            "owner=ay" in out.stdout and "ay-exp-301" in out.stdout, out.stdout + out.stderr)
    out = kx("new", "EXP-210", "--note", "codex deneyi")
    kontrol("atanmamis yuzluk: Codex slug'i degismedi", "as-cx-exp-210" in out.stdout, out.stdout)

    print("\n--- 8) gurultu tabani ---")
    def oneri(o):
        return o.stdout.split("ONERI:")[-1].splitlines()[0] if "ONERI:" in o.stdout else ""

    kucuk = dict(temel, exp_id="EXP-050", parent="EXP-001",
                 fold_scores=[x + 1e-5 for x in temel["fold_scores"]],
                 cv_mean=temel["cv_mean"] + 1e-5, cv_oof=temel["cv_oof"] + 1e-5)
    deney_kur("EXP-050", kucuk, gecerli_submission())
    kx("kayit", "EXP-050")
    out = kx("cmp", "EXP-050")
    kontrol("taban yokken: her fold +1e-5 -> KABUL + olculmedi uyarisi",
            "KABUL" in oneri(out) and "gurultu tabani olculmedi" in out.stdout, out.stdout)

    gur = dict(temel, exp_id="EXP-060", parent="EXP-001", seed=7,
               fold_scores=[0.905, 0.905, 0.885, 0.9, 0.91])
    deney_kur("EXP-060", gur, gecerli_submission())
    kx("kayit", "EXP-060")
    out = kx("gurultu", "EXP-060")
    nf = json.loads(cfg_yol.read_text(encoding="utf-8")).get("noise_floor")
    kontrol("gurultu: kx.json noise_floor yazildi", out.returncode == 0 and isinstance(nf, float) and nf > 0,
            out.stdout + out.stderr)
    out = kx("cmp", "EXP-050")
    kontrol("gurultu icindeki fark -> KABUL onerilmedi",
            "KABUL" not in oneri(out) and "GURULTU ICINDE" in out.stdout, out.stdout)

    ayni = dict(temel, exp_id="EXP-061", parent="EXP-001")
    deney_kur("EXP-061", ayni, gecerli_submission())
    kx("kayit", "EXP-061")
    out = kx("gurultu", "EXP-061")
    kontrol("ayni seed -> gurultu olcumu reddedildi", out.returncode != 0 and "seed" in out.stderr, out.stderr)
    cfg = json.loads(cfg_yol.read_text(encoding="utf-8"))
    cfg["noise_floor"] = None
    cfg_yol.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    print("\n--- 9) uctan uca yerel kosu (fold-ici TE + teknik listesi) ---")
    def yerel_deney(exp, not_, degistir):
        kx("new", exp, "--note", not_, "--target", "y_ham", "--pos-label", "Yes")
        yol = SCRATCH / "experiments" / exp / "code.py"
        kod = yol.read_text(encoding="utf-8")
        for eski, yeni in degistir:
            assert eski in kod, eski
            kod = kod.replace(eski, yeni, 1)
        yol.write_text(kod, encoding="utf-8")
        return subprocess.run([sys.executable, str(yol)], capture_output=True, text=True,
                              encoding="utf-8", errors="replace")

    te_kodu = ("    ort = pd.Series(ytr, index=Xtr.index).groupby(Xtr['b']).mean()\n"
               "    for d in (Xtr, Xva, Xte):\n"
               "        d['b_te'] = d['b'].map(ort).astype(float)\n"
               "    return Xtr, Xva, Xte")
    r = yerel_deney("EXP-070", "fold-ici TE", [
        ("TEKNIKLER = [\n", "TEKNIKLER = [\n    'fold-ici target encoding (b) . test . yalniz egitim fold''unda fit',\n"),
        ("    # TODO(deney): fold-ici donusumler buraya (yoksa oldugu gibi birak)\n    return Xtr, Xva, Xte", te_kodu),
    ])
    kontrol("yerel kosu tamamlandi", r.returncode == 0 and "=== KX RESULT SONU ===" in r.stdout,
            r.stdout[-600:] + r.stderr[-1500:])
    kontrol("uygulanan teknikler ekrana basildi", "fold-ici target encoding (b)" in r.stdout, r.stdout[:600])
    kontrol("oof.parquet yerelde yazildi", (SCRATCH / "experiments" / "EXP-070" / "output" / "oof.parquet").exists())
    out = kx("kayit", "EXP-070")
    kontrol("yerel kosu -> kayit GECTI, oof kontrolu atlanmadi",
            out.returncode == 0 and "DOGRULAMA GECTI" in out.stdout and "oof.parquet kontrolu" not in out.stdout,
            out.stdout + out.stderr)
    kontrol("kayit teknikleri gosterdi", "fold-ici target encoding (b)" in out.stdout, out.stdout)

    r = yerel_deney("EXP-071", "seed 7", [("\nSEED = 42", "\nSEED = 7")])
    kontrol("ikinci yerel kosu tamamlandi", r.returncode == 0, r.stderr[-1500:])
    kx("kayit", "EXP-071")

    print("\n--- 10) blend ---")
    def blend(*a):
        return subprocess.run([sys.executable, str(SCRATCH / "tools" / "blend.py"), *a],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
    r = blend("EXP-070", "EXP-071")
    kontrol("blend: iki yerel OOF birlesti (id + y kolonlu OOF)", r.returncode == 0 and "KARAR" in r.stdout,
            r.stdout + r.stderr)
    r = blend("EXP-070", "EXP-071", "--rank")
    kontrol("blend --rank calisti", r.returncode == 0 and "RANK modu" in r.stdout, r.stdout + r.stderr)

    print("\n--- 11) adversarial validation ---")
    def adv(*a):
        return subprocess.run([sys.executable, str(SCRATCH / "tools" / "adv_val.py"), *a],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")

    def auc_ve_ilk(o):
        auc = float(o.stdout.split("ADVERSARIAL AUC:")[1].split()[0])
        ilk = o.stdout.split("kolon (permutation importance")[1].splitlines()[1].split()[0]
        return auc, ilk

    r = adv("--drop", "grp,t")
    ok = r.returncode == 0 and "ADVERSARIAL AUC" in r.stdout
    kontrol("adv_val ayni dagilim -> AUC < 0.65", ok and auc_ve_ilk(r)[0] < 0.65, r.stdout + r.stderr)
    kayik = pd.read_csv(SCRATCH / "data" / "test.csv")
    kayik["a"] = kayik["a"] + 0.5
    kayik.to_csv(SCRATCH / "data" / "test_kayik.csv", index=False)
    r = adv("--test", str(SCRATCH / "data" / "test_kayik.csv"), "--drop", "grp,t")
    ok = r.returncode == 0 and "ADVERSARIAL AUC" in r.stdout
    kontrol("adv_val kaydirilmis 'a' -> AUC > 0.8 ve 'a' ilk sirada",
            ok and auc_ve_ilk(r)[0] > 0.8 and auc_ve_ilk(r)[1] == "a", r.stdout + r.stderr)

    print("\n--- 12) fold semalari (make_folds.py) ---")
    snip = SCRATCH / "core" / "folds_snippet.py"
    orj = snip.read_text(encoding="utf-8")
    tr = pd.read_csv(SCRATCH / "data" / "train.csv")
    for sema, arg in (("kfold", ["--target", "a"]),
                      ("stratified_reg", ["--target", "a"]),
                      ("group", ["--target", "y_ham", "--pos", "Yes", "--group", "grp"]),
                      ("stratified_group", ["--target", "y_ham", "--pos", "Yes", "--group", "grp"]),
                      ("time", ["--target", "y_ham", "--pos", "Yes", "--time", "t"])):
        snip.write_text(orj.replace('FOLD_SCHEME = "stratified"', f'FOLD_SCHEME = "{sema}"', 1), encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRATCH / "tools" / "make_folds.py"), *arg, "--force"],
                           capture_output=True, text=True, cwd=SCRATCH, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            kontrol(f"sema {sema} uretildi", False, r.stderr)
            continue
        f = pd.read_csv(SCRATCH / "core" / "folds.csv")["fold"].values
        if "group" in sema:
            cakisan = sum(len(set(f[tr["grp"].values == g])) > 1 for g in tr["grp"].unique())
            kontrol(f"sema {sema}: hicbir grup iki fold'da degil", cakisan == 0, f"{cakisan} grup")
        elif sema == "time":
            t = tr["t"].values
            ok = all(t[f < k].max() < t[f == k].min() for k in range(5))
            kontrol("sema time: validasyon her zaman egitimden sonra, ilk blok -1", ok and (f == -1).any())
        else:
            kontrol(f"sema {sema}: 5 fold, bos satir yok", sorted(set(f)) == [0, 1, 2, 3, 4])

    print("\n--- 13) time semasi uctan uca (ilk blok tahminsiz) ---")
    snip.write_text(orj.replace('FOLD_SCHEME = "stratified"', 'FOLD_SCHEME = "time"', 1), encoding="utf-8")
    subprocess.run([sys.executable, str(SCRATCH / "tools" / "make_folds.py"), "--target", "y_ham",
                    "--pos", "Yes", "--time", "t", "--force"], capture_output=True, cwd=SCRATCH)
    cfg = json.loads(cfg_yol.read_text(encoding="utf-8"))
    cfg["time_col"] = "t"
    cfg_yol.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    r = yerel_deney("EXP-080", "time semasi", [])
    kontrol("time: yerel kosu tamamlandi", r.returncode == 0, r.stderr[-1500:])
    out = kx("kayit", "EXP-080")
    kontrol("time: kayit GECTI (OOF satiri = fold >= 0 satiri)",
            out.returncode == 0 and "DOGRULAMA GECTI" in out.stdout, out.stdout + out.stderr)
    r = blend("EXP-080")
    kontrol("time: blend -1 blogunu disarida birakti", r.returncode == 0 and "UYARI" not in r.stdout,
            r.stdout + r.stderr)
    snip.write_text(orj, encoding="utf-8")

    print(f"\n==== SONUC: {len(gecti)} gecti, {len(kaldi)} kaldi ====")
    if kaldi:
        for k in kaldi:
            print(f"  KALDI: {k}")
        sys.exit(1)


if __name__ == "__main__":
    main()
