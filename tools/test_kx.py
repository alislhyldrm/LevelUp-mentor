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
    train.to_csv(SCRATCH / "data" / "train.csv", index=False)
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
        kontrol("yer tutucu kalmadi", "__" + "FOLD_SNIPPET__" not in kod and "__" + "TARGET__" not in kod)

    out = kx("board")
    kontrol("board Kaggle cagirmadan calisti", out.returncode == 0, out.stderr)
    kontrol("board yerel parmak izini gosteriyor", fp in out.stdout, out.stdout)

    print(f"\n==== SONUC: {len(gecti)} gecti, {len(kaldi)} kaldi ====")
    if kaldi:
        for k in kaldi:
            print(f"  KALDI: {k}")
        sys.exit(1)


if __name__ == "__main__":
    main()
