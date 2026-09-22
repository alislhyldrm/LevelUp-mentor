#!/usr/bin/env python
"""kx - Kaggle deney dongusu.

Notebook uret -> Kaggle'a push -> durum -> ciktiyi indir + DOGRULA -> parent ile karsilastir.
Insan kuryeligi yapmaz; dosya tasima islemi kalmaz.

Komutlar:
    kx.py new   EXP-017 --parent EXP-012 --note "target encoding" [--owner codex]
    kx.py push  EXP-017 [--gpu] [--internet] [--dataset user/slug ...]
    kx.py status [EXP-017]
    kx.py fetch EXP-017
    kx.py cmp   EXP-017
    kx.py board

Ayarlar: repo kokundeki kx.json. Eksikse `kx.py board` sablonunu yazar.
Submit YOK. Bu betik hicbir kosulda Kaggle'a gonderim yapmaz.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "kx.json"
SLUGS_PATH = ROOT / "log" / "slugs.json"
RUNS_PATH = ROOT / "log" / "RUNS.md"
SUMMARY_PATH = ROOT / "experiments" / "EXP_SUMMARY.md"
FOLDS_PATH = ROOT / "core" / "folds.csv"
TEMPLATE_PATH = ROOT / "tools" / "notebook_template.ipynb"

CONFIG_TEMPLATE = {
    "username": "",
    "initials": "as",
    "competition": "",
    "core_dataset": "",
    "main_score": "cv_mean",
    "greater_is_better": True,
}


# ---------------------------------------------------------------- yardimcilar

def die(msg: str) -> None:
    print(f"HATA: {msg}", file=sys.stderr)
    sys.exit(1)


def now() -> str:
    return datetime.now().strftime("%H:%M")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(CONFIG_TEMPLATE, indent=2), encoding="utf-8")
        die(f"{CONFIG_PATH.name} yoktu, sablon yazildi. username ve competition alanlarini doldur.")
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    for key in ("username", "initials"):
        if not cfg.get(key):
            die(f"kx.json icinde '{key}' bos. Doldur.")
    return cfg


def load_slugs() -> dict:
    if SLUGS_PATH.exists():
        return json.loads(SLUGS_PATH.read_text(encoding="utf-8"))
    return {}


def save_slugs(data: dict) -> None:
    SLUGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SLUGS_PATH.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def kaggle(*args: str, check: bool = True, timeout: int = 180) -> subprocess.CompletedProcess:
    exe = shutil.which("kaggle")
    if not exe:
        die("kaggle CLI bulunamadi. `pip install kaggle` ve token kurulumu gerekli.")
    proc = subprocess.run(
        [exe, *args], capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace"
    )
    if check and proc.returncode != 0:
        die(f"kaggle {' '.join(args)}\n{proc.stdout}\n{proc.stderr}")
    return proc


def exp_dir(exp_id: str) -> Path:
    return ROOT / "experiments" / exp_id


def normalize_exp(raw: str) -> str:
    m = re.fullmatch(r"(?:EXP-?)?(\d{1,3})", raw.strip(), re.IGNORECASE)
    if not m:
        die(f"Gecersiz deney kimligi: {raw!r}. Ornek: EXP-017")
    return f"EXP-{int(m.group(1)):03d}"


def exp_number(exp_id: str) -> int:
    return int(exp_id.split("-")[1])


def owner_of(exp_id: str) -> str:
    """CODEX.md kimlik ayrimi: EXP-2xx Codex'in, gerisi Claude'un."""
    return "codex" if 200 <= exp_number(exp_id) < 300 else "claude"


def slug_for(exp_id: str, cfg: dict) -> str:
    tag = "cx" if owner_of(exp_id) == "codex" else "cl"
    return f"{cfg['initials']}-{tag}-exp-{exp_number(exp_id):03d}"


def read_result(exp_id: str) -> dict | None:
    path = exp_dir(exp_id) / "output" / "result.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        die(f"{path} okunamadi: {exc}")


def append_line(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + line + "\n", encoding="utf-8")


# ---------------------------------------------------------------------- new

MINIMAL_NOTEBOOK = {
    "cells": [],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


def md_cell(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def cmd_new(args, cfg) -> None:
    exp_id = normalize_exp(args.exp)
    parent = normalize_exp(args.parent) if args.parent else "-"
    d = exp_dir(exp_id)
    if d.exists():
        die(f"{exp_id} zaten var. Sonucu alinmis deney degistirilmez, yeni deney ac (CLAUDE.md kural 4).")
    d.mkdir(parents=True)
    (d / "output").mkdir()

    owner = owner_of(exp_id)
    slug = slug_for(exp_id, cfg)

    if TEMPLATE_PATH.exists():
        raw = TEMPLATE_PATH.read_text(encoding="utf-8")
        for token, value in (
            ("__EXP_ID__", exp_id),
            ("__PARENT__", parent),
            ("__OWNER__", owner),
            ("__SLUG__", slug),
            ("__NOTE__", (args.note or "TODO").replace('"', "'")),
        ):
            raw = raw.replace(token, value)
        nb = json.loads(raw)
    else:
        nb = json.loads(json.dumps(MINIMAL_NOTEBOOK))
        print(f"UYARI: {TEMPLATE_PATH.name} yok, bos notebook uretildi.")

    meta = (
        f"# {exp_id}\n"
        f"- parent: {parent}\n"
        f"- owner: {owner}\n"
        f"- slug: {slug}\n"
        f"- hipotez: {args.note or 'TODO'}\n"
        f"- mod: FAST | FULL (sec)\n"
        f"- seed: 42\n"
        f"- GPU: hayir | internet: hayir\n"
        f"- eklenecek girdiler: hackathon-core\n"
        f"- tahmini sure: TODO-TODO dk (tek sayi degil, aralik)\n"
    )
    nb["cells"].insert(0, md_cell(meta))
    (d / "notebook.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")

    card = (
        f"# {exp_id}  (parent: {parent} | kesif? hayir)\n"
        f"- Owner: {owner} | Slug: {slug} | Kaggle versiyon: - | Kosu: hazirlaniyor\n"
        f"- Hipotez: {args.note or 'TODO'}\n"
        f"- Degisiklik: TODO (parent'a gore tam olarak ne)\n"
        f"- Mod/Seed/GPU: TODO / 42 / hayir\n"
        f"- Sonuc: -\n"
        f"- Karar: -\n"
        f"- Codex incelemesi: yok\n"
        f"- Ders: -\n"
    )
    (d / "card.md").write_text(card, encoding="utf-8")

    metadata = {
        "id": f"{cfg['username']}/{slug}",
        # BASLIK = SLUG, baska bir sey degil. Kaggle kernel'in GERCEK slug'ini
        # id alanindan degil, baslikten kendi slugify'iyla turetir; ikisi
        # uyusmazsa Kaggle sessizce KENDI slug'ini kullanir ve id yoksayilir
        # (provada yakalandi: not metinli baslik -> beklenmedik slug -> status/
        # fetch "permission denied" gibi yaniltici hatayla patlar). Hipotez notu
        # card.md'de zaten var; baslikte tekrar etmeye gerek yok.
        "title": slug,
        "code_file": "notebook.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": False,
        "enable_tpu": False,
        "enable_internet": False,
        "dataset_sources": [s for s in [cfg.get("core_dataset")] if s],
        "competition_sources": [s for s in [cfg.get("competition")] if s],
        "kernel_sources": [],
        "model_sources": [],
    }
    (d / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"{exp_id} olusturuldu  ->  {d}")
    print(f"  owner={owner}  slug={slug}  parent={parent}")
    print("  Siradaki: notebook.ipynb'i doldur, sonra `kx.py push` et.")


# --------------------------------------------------------------------- push

def slug_exists_remotely(slug: str, cfg: dict) -> bool:
    proc = kaggle("kernels", "status", f"{cfg['username']}/{slug}", check=False, timeout=90)
    out = (proc.stdout + proc.stderr).lower()
    return proc.returncode == 0 and "404" not in out and "not found" not in out


def check_notebook_syntax(nb_path: Path) -> None:
    """Her kod hucresini ast.parse ile denetler - push'tan once, saniyeler icinde.
    Provada bulundu: bir syntax hatasi Kaggle kuyruguna girip ~5 dk sonra
    hata olarak dondu. Bunu yerelde yakalamak o turu tamamen ortadan kaldirir."""
    import ast

    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    errs = []
    for i, c in enumerate(nb.get("cells", [])):
        if c.get("cell_type") != "code":
            continue
        src = "".join(c.get("source", []))
        try:
            ast.parse(src)
        except SyntaxError as e:
            errs.append(f"  hucre {i}, satir {e.lineno}: {e.msg}\n    {(e.text or '').strip()}")
    if errs:
        die("notebook.ipynb'de syntax hatasi var, push edilmedi:\n" + "\n".join(errs))


def cmd_push(args, cfg) -> None:
    exp_id = normalize_exp(args.exp)
    d = exp_dir(exp_id)
    meta_path = d / "kernel-metadata.json"
    if not meta_path.exists():
        die(f"{exp_id} icin kernel-metadata.json yok. Once `kx.py new`.")

    check_notebook_syntax(d / "notebook.ipynb")

    slug = slug_for(exp_id, cfg)
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))

    # --- kimlik dogrulamasi: paylasilan hesapta ustune yazma felaketini onler
    expected_id = f"{cfg['username']}/{slug}"
    if metadata.get("id") != expected_id:
        die(f"kernel-metadata.json id '{metadata.get('id')}' beklenen '{expected_id}' degil. Elle duzeltme yapma, `kx.py new` kullan.")

    slugs = load_slugs()
    if slug in slugs and slugs[slug] != exp_id:
        die(f"'{slug}' slug'i {slugs[slug]} deneyine kayitli. {exp_id} icin push durduruldu.")
    if slug not in slugs and slug_exists_remotely(slug, cfg):
        die(
            f"'{slug}' Kaggle hesabinda ZATEN VAR ama yerel kaydi yok.\n"
            "  Paylasilan hesapta baskasinin kosusunun ustune yazilabilir.\n"
            f"  Kontrol et: kaggle kernels status {expected_id}"
        )

    metadata["enable_gpu"] = bool(args.gpu)
    metadata["enable_internet"] = bool(args.internet)
    for ds in args.dataset or []:
        if ds not in metadata["dataset_sources"]:
            metadata["dataset_sources"].append(ds)
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"push: {expected_id}  gpu={args.gpu}  internet={args.internet}")
    proc = kaggle("kernels", "push", "-p", str(d), timeout=600)
    print(proc.stdout.strip())
    if "does not resolve to the specified id" in (proc.stdout + proc.stderr):
        print(f"UYARI: Kaggle baslik/id uyumsuzlugu bildirdi. Gercek slug '{slug}' olmayabilir.")

    # Push "basarili" desin bile, Kaggle GERCEKTE farkli bir slug uretmis olabilir
    # (baslik id'ye tam slugify olmuyorsa). Burada dogrulanmazsa hata ilk `fetch`'te,
    # yanlis dosya beklerken cikar - o zaman teshisi cok daha zor.
    check = kaggle("kernels", "status", expected_id, check=False, timeout=60)
    if check.returncode != 0:
        real = kaggle("kernels", "list", "--mine", "--search", slug, check=False, timeout=60)
        die(
            f"push sonrasi '{expected_id}' erisilemiyor - Kaggle farkli bir slug uretmis olabilir.\n"
            f"  {check.stdout.strip() or check.stderr.strip()}\n"
            f"  '{slug}' icin bulunanlar:\n  {real.stdout.strip()[:400]}"
        )

    slugs[slug] = exp_id
    save_slugs(slugs)

    append_line(
        RUNS_PATH,
        f"| {slug} | {owner_of(exp_id)} | {now()} | {'evet' if args.gpu else 'hayir'} | ? | kosuyor |",
    )
    print(f"log/RUNS.md guncellendi. Durum: `kx.py status {exp_id}`")


# ------------------------------------------------------------------- status

def cmd_status(args, cfg) -> None:
    targets = [normalize_exp(args.exp)] if args.exp else sorted(load_slugs().values())
    if not targets:
        print("Kayitli kosu yok.")
        return
    for exp_id in targets:
        slug = slug_for(exp_id, cfg)
        proc = kaggle("kernels", "status", f"{cfg['username']}/{slug}", check=False, timeout=90)
        line = (proc.stdout or proc.stderr).strip().replace("\n", " ")
        print(f"{exp_id:9} {slug:24} {line[:100]}")


# -------------------------------------------------------------------- fetch

def _read_table(path: Path):
    import pandas as pd

    return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)


def validate_output(exp_id: str, out: Path) -> list[str]:
    """Bolum 4.2 sozlesmesi. Donen liste bossa sonuc kayda girebilir."""
    errs: list[str] = []
    result = read_result(exp_id)
    if result is None:
        return [f"result.json yok ({out / 'result.json'})"]

    # FAST sabit bir alt kumede kosar (core/cv_spec.md): satir ve fold sayisi
    # bilerek eksiktir. Tam CV kontrolleri yalniz FULL icin uygulanir.
    is_full = str(result.get("mode", "")).upper() == "FULL"

    expected_rows = None
    expected_folds = None
    if FOLDS_PATH.exists():
        try:
            folds = _read_table(FOLDS_PATH)
            expected_rows = len(folds)
            if "fold" in folds.columns:
                expected_folds = int(folds["fold"].nunique())
        except Exception as exc:  # noqa: BLE001
            errs.append(f"core/folds.csv okunamadi: {exc}")

    for name, need_rows in (("oof.parquet", True), ("test_preds.parquet", False)):
        path = out / name
        if not path.exists():
            errs.append(f"{name} yok")
            continue
        try:
            df = _read_table(path)
        except Exception as exc:  # noqa: BLE001
            errs.append(f"{name} okunamadi: {exc}")
            continue
        if "id" not in df.columns:
            errs.append(f"{name}: 'id' kolonu yok (kimliksiz tahmin yasak)")
            continue
        if df["id"].duplicated().any():
            errs.append(f"{name}: tekrar eden id var ({int(df['id'].duplicated().sum())} satir)")
        pred_cols = [c for c in df.columns if c not in ("id", "fold")]
        if not pred_cols:
            errs.append(f"{name}: tahmin kolonu yok")
        elif df[pred_cols].isna().any().any():
            errs.append(f"{name}: tahmin kolonlarinda NaN var")
        if need_rows and is_full and expected_rows is not None and len(df) != expected_rows:
            errs.append(f"{name}: {len(df)} satir, folds.csv {expected_rows} satir - hizalama bozuk")

    if not (out / "submission.csv").exists():
        errs.append("submission.csv yok")

    for field in ("exp_id", "cv_mean", "cv_oof", "fold_scores", "n_folds_done"):
        if field not in result:
            errs.append(f"result.json: '{field}' alani yok")

    # Skorlar sonlu olmali. Provada olculdu: sklearn roc_auc_score tek sinifli bir
    # dilimde hata vermez, NAN doner. Kucuk FAST fold'lari veya nadir sinif dilimleri
    # boyle bir skoru sessizce kayda sokabilir.
    def _finite(v) -> bool:
        return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and abs(v) != float("inf")

    for field in ("cv_mean", "cv_oof"):
        if field in result and not _finite(result[field]):
            errs.append(f"result.json: {field}={result[field]!r} sonlu bir sayi degil (nan/inf?)")
    scores = result.get("fold_scores")
    if isinstance(scores, list):
        bad = [i for i, v in enumerate(scores) if not _finite(v)]
        if bad:
            errs.append(f"result.json: fold_scores {bad} sonlu degil - o fold'da tek sinif veya bos dilim var")
    elif "fold_scores" in result:
        errs.append("result.json: 'fold_scores' liste degil")
    if result.get("exp_id") not in (None, exp_id):
        errs.append(f"result.json exp_id '{result.get('exp_id')}' klasor {exp_id} ile uyusmuyor")
    if is_full and expected_folds is not None and result.get("n_folds_done") not in (None, expected_folds):
        errs.append(f"result.json n_folds_done={result.get('n_folds_done')}, beklenen {expected_folds} - FULL kosuda eksik fold")
    if not result.get("mode"):
        errs.append("result.json: 'mode' alani yok (FAST/FULL ayrimi yapilamaz)")
    return errs


def cmd_fetch(args, cfg) -> None:
    exp_id = normalize_exp(args.exp)
    d = exp_dir(exp_id)
    if not d.exists():
        die(f"{exp_id} klasoru yok.")
    out = d / "output"
    out.mkdir(exist_ok=True)
    slug = slug_for(exp_id, cfg)

    print(f"indiriliyor: {cfg['username']}/{slug} -> {out}")
    kaggle("kernels", "output", f"{cfg['username']}/{slug}", "-p", str(out), timeout=900)

    errs = validate_output(exp_id, out)
    if errs:
        print("\nDOGRULAMA BASARISIZ - sonuc kayda GIRMEDI:")
        for e in errs:
            print(f"  - {e}")
        print("\nOnce bunu duzelt. Bozuk hizalama gece yarisi fark edilirse tum gecmisi cope atar.")
        sys.exit(1)

    result = read_result(exp_id)
    main_key = cfg.get("main_score", "cv_mean")
    score = result.get(main_key)
    folds = result.get("fold_scores") or []
    row = (
        f"| {exp_id} | {result.get('owner', owner_of(exp_id))} | {result.get('parent', '-')} "
        f"| {result.get('mode', '-')} | {score} | {result.get('cv_mean')} | {result.get('cv_oof')} "
        f"| {len(folds)} | {result.get('runtime_min', '-')} | - "
        f"| {result.get('kernel_slug', slug)} / v{result.get('kernel_version', '?')} |"
    )
    append_line(SUMMARY_PATH, row)

    print(f"\nDOGRULAMA GECTI. {exp_id} ana skor ({main_key}): {score}")
    print(f"fold skorlari: {folds}")
    print(f"EXP_SUMMARY.md guncellendi. Siradaki: `kx.py cmp {exp_id}`")


# ---------------------------------------------------------------------- cmp

def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def _std(xs):
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def cmd_cmp(args, cfg) -> None:
    exp_id = normalize_exp(args.exp)
    child = read_result(exp_id)
    if child is None:
        die(f"{exp_id} icin result.json yok. Once `kx.py fetch`.")

    parent_id = args.parent or child.get("parent")
    if not parent_id or parent_id == "-":
        die(f"{exp_id} icin parent yok. Karsilastirma yapilamaz.")
    parent_id = normalize_exp(parent_id)
    parent = read_result(parent_id)
    if parent is None:
        die(f"{parent_id} icin result.json yok.")

    if child.get("mode") != parent.get("mode"):
        print(f"UYARI: modlar farkli ({child.get('mode')} vs {parent.get('mode')}). "
              "FAST sonuclari yalniz FAST ile karsilastirilir.")

    key = cfg.get("main_score", "cv_mean")
    other_key = "cv_oof" if key == "cv_mean" else "cv_mean"
    gib = bool(cfg.get("greater_is_better", True))
    cs, ps = child.get(key), parent.get(key)
    if cs is None or ps is None:
        die(f"Ana skor '{key}' iki result.json'dan birinde yok.")

    cf, pf = child.get("fold_scores") or [], parent.get("fold_scores") or []
    sign = 1.0 if gib else -1.0
    main_diff = (cs - ps) * sign

    print(f"\n{exp_id} vs {parent_id}   (ana skor: {key}, {'buyuk iyi' if gib else 'kucuk iyi'})")
    print(f"  {exp_id}: {cs}")
    print(f"  {parent_id}: {ps}")
    print(f"  fark: {main_diff:+.6f}")

    # Diger skor bilgi amacli her zaman gosterilir; secilmedi diye kaybolmaz.
    # Iki skor zit yone isaret ediyorsa (biri iyilesme, digeri kotulesme derse)
    # otomatik oneri bunu gormez - insan burada uyarilir.
    co, po = child.get(other_key), parent.get(other_key)
    if co is not None and po is not None:
        other_diff = (co - po) * sign
        print(f"  ({other_key}: {exp_id}={co}  {parent_id}={po}  fark={other_diff:+.6f})")
        if main_diff != 0 and other_diff != 0 and (main_diff > 0) != (other_diff > 0):
            print(f"\n  UYARI: {key} ve {other_key} ZIT yone isaret ediyor "
                  f"({key} {'iyilesme' if main_diff>0 else 'kotulesme'}, "
                  f"{other_key} {'iyilesme' if other_diff>0 else 'kotulesme'}). "
                  "Otomatik oneri yalniz ana skora bakar - karari vermeden once ikisine de bak.")

    suggestion = "kanit yetersiz - fold skorlari eksik"
    if len(cf) == len(pf) and cf:
        diffs = [(c - p) * sign for c, p in zip(cf, pf)]
        sd = _std(diffs)
        md = _mean(diffs)
        print("\n  fold | " + parent_id + " | " + exp_id + " | fark")
        for i, (p, c, dd) in enumerate(zip(pf, cf, diffs)):
            print(f"  {i:>4} | {p:>10.6f} | {c:>10.6f} | {dd:+.6f}")
        print(f"\n  ortalama fark: {md:+.6f}   fold farklarinin std: {sd:.6f}")
        wins = sum(1 for dd in diffs if dd > 0)
        print(f"  iyilesen fold: {wins}/{len(diffs)}")

        if wins == len(diffs) or (md > 0 and sd > 0 and md > 2 * sd):
            suggestion = "KABUL - yeni ana hat"
        elif md > 0:
            suggestion = "HAVUZ - ana hat degismez, OOF ensemble adayi. Farkli seed ile tekrar kosma."
        else:
            suggestion = "RED - OOF yine saklanir, silinmez"
        if abs(md) < sd / 4:
            suggestion += "  (fark kucuk: daha basit/hizli model korunur)"

    print(f"\n  ONERI: {suggestion}")
    print(f"  Karari insan verir. card.md'ye yaz, STATUS.md'yi guncelle.")


# -------------------------------------------------------------------- board

def cmd_board(args, cfg) -> None:
    print(f"=== KX BOARD  {datetime.now().strftime('%a %H:%M')} ===\n")

    slugs = load_slugs()
    print("-- Kaggle'da kayitli kosular --")
    if not slugs:
        print("  (yok)")
    else:
        for slug, exp_id in sorted(slugs.items()):
            proc = kaggle("kernels", "status", f"{cfg['username']}/{slug}", check=False, timeout=60)
            line = (proc.stdout or proc.stderr).strip().replace("\n", " ")
            print(f"  {exp_id:9} {slug:24} {line[:80]}")

    print("\n-- Son sonuclar --")
    results = []
    for d in sorted((ROOT / "experiments").glob("EXP-*")):
        r = read_result(d.name)
        if r:
            results.append((d.name, r))
    if not results:
        print("  (yok)")
    else:
        key = cfg.get("main_score", "cv_mean")
        gib = bool(cfg.get("greater_is_better", True))
        for name, r in results[-10:]:
            print(f"  {name:9} {r.get('mode','-'):5} {key}={r.get(key)}  ({r.get('owner','-')})")
        scored = [(n, r) for n, r in results if isinstance(r.get(key), (int, float))]
        if scored:
            best = (max if gib else min)(scored, key=lambda t: t[1][key])
            print(f"\n  EN IYI ADAY: {best[0]}  {key}={best[1][key]}")

    print("\n-- Hatirlatma --")
    print("  Submit etme. Oner, insan gonderir, log/SUBMISSIONS.md'ye yazilir.")
    print("  GPU gerektirmeyen her sey CPU'da kosar.")


# --------------------------------------------------------------------- main

def main() -> None:
    p = argparse.ArgumentParser(prog="kx", description="Kaggle deney dongusu. Submit yapmaz.")
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="deney klasoru + notebook + kernel-metadata uret")
    n.add_argument("exp")
    n.add_argument("--parent")
    n.add_argument("--note")
    n.set_defaults(fn=cmd_new)

    u = sub.add_parser("push", help="Kaggle'a batch kosu baslat")
    u.add_argument("exp")
    u.add_argument("--gpu", action="store_true")
    u.add_argument("--internet", action="store_true")
    u.add_argument("--dataset", action="append")
    u.set_defaults(fn=cmd_push)

    s = sub.add_parser("status", help="kosu durumlari")
    s.add_argument("exp", nargs="?")
    s.set_defaults(fn=cmd_status)

    f = sub.add_parser("fetch", help="ciktiyi indir ve DOGRULA")
    f.add_argument("exp")
    f.set_defaults(fn=cmd_fetch)

    c = sub.add_parser("cmp", help="parent ile fold fold karsilastir")
    c.add_argument("exp")
    c.add_argument("--parent")
    c.set_defaults(fn=cmd_cmp)

    b = sub.add_parser("board", help="tek ekran")
    b.set_defaults(fn=cmd_board)

    args = p.parse_args()
    args.fn(args, load_config())


if __name__ == "__main__":
    main()
