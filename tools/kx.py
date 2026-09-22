#!/usr/bin/env python
"""kx - deney dongusu (Kaggle'a GONDERIM YOK).

    kod uret -> insan Kaggle'da kosturur -> ekran ciktisi yapistirilir
    -> DOGRULA -> parent ile karsilastir -> kaydet

Komutlar:
    kx.py new   EXP-017 --parent EXP-012 --note "charging_total" [--target ... --id-col ...]
    kx.py kayit EXP-017            # output/ icindekini dogrula + EXP_SUMMARY'ye yaz
    kx.py cmp   EXP-017            # parent ile fold fold karsilastir
    kx.py board                    # tek ekran

Bu betik Kaggle CLI'yi HIC cagirmaz: ne kernel push, ne dataset yukleme, ne gonderim.
Kaggle'a giden tek sey, insanin notebook'a kendi elleriyle yapistirdigi koddur.
Ayarlar: repo kokundeki kx.json.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "kx.json"
RUNS_PATH = ROOT / "log" / "RUNS.md"
SUMMARY_PATH = ROOT / "experiments" / "EXP_SUMMARY.md"
FOLDS_PATH = ROOT / "core" / "folds.csv"
SNIPPET_PATH = ROOT / "core" / "folds_snippet.py"
METRIC_PATH = ROOT / "core" / "metric.py"
TEMPLATE_PATH = ROOT / "tools" / "code_template.py"

CONFIG_TEMPLATE = {
    "initials": "as",
    "competition": "",
    "target": "",
    "id_col": "id",
    "pos_label": "",
    "sample_submission": "data/sample_submission.csv",
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
        die(f"{CONFIG_PATH.name} yoktu, sablon yazildi. Alanlari doldur.")
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if not cfg.get("initials"):
        die("kx.json icinde 'initials' bos. Tek ortak hesapta slug cakismasini bu onler.")
    return cfg


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
    """Kaggle notebook adi. Tek ortak hesapta 6 kisi calisiyor - cakisma olmasin."""
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
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_text(text + line + "\n", encoding="utf-8")


def _read_table(path: Path):
    import pandas as pd

    return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)


def local_fingerprint() -> str | None:
    """core/folds.csv'nin parmak izi. Kaggle kosusu ayni izi basmali."""
    if not FOLDS_PATH.exists() or not SNIPPET_PATH.exists():
        return None
    sys.path.insert(0, str(SNIPPET_PATH.parent))
    try:
        import numpy as np
        from folds_snippet import fold_fingerprint

        folds = _read_table(FOLDS_PATH)
        return fold_fingerprint(np.asarray(folds["fold"], dtype="int64"))
    except Exception as exc:  # noqa: BLE001
        print(f"UYARI: yerel fold parmak izi hesaplanamadi: {exc}")
        return None


# ---------------------------------------------------------------------- new

def cmd_new(args, cfg) -> None:
    exp_id = normalize_exp(args.exp)
    parent = normalize_exp(args.parent) if args.parent else "-"
    d = exp_dir(exp_id)
    if d.exists():
        die(f"{exp_id} zaten var. Sonucu alinmis deney degistirilmez, yeni deney ac (CLAUDE.md kural 4).")

    if not TEMPLATE_PATH.exists():
        die(f"{TEMPLATE_PATH} yok. Sablon olmadan deney acilmaz.")
    if not SNIPPET_PATH.exists():
        die(f"{SNIPPET_PATH} yok. Fold sozlesmesi olmadan deney acilmaz (once D-01).")
    if not METRIC_PATH.exists():
        die(f"{METRIC_PATH} yok. Metrik olmadan deney acilmaz (once D-01).")

    d.mkdir(parents=True)
    (d / "output").mkdir()

    owner = owner_of(exp_id)
    slug = slug_for(exp_id, cfg)
    note = (args.note or "TODO").replace('"', "'")

    code = TEMPLATE_PATH.read_text(encoding="utf-8")
    for token, value in (
        ("__FOLD_SNIPPET__", SNIPPET_PATH.read_text(encoding="utf-8").strip()),
        ("__METRIC_SNIPPET__", METRIC_PATH.read_text(encoding="utf-8").strip()),
        ("__EXP_ID__", exp_id),
        ("__PARENT__", parent),
        ("__OWNER__", owner),
        ("__SLUG__", slug),
        ("__NOTE__", note),
        ("__TARGET__", args.target or cfg.get("target", "")),
        ("__IDCOL__", args.id_col or cfg.get("id_col", "id")),
        ("__POS_LABEL__", args.pos_label if args.pos_label is not None else cfg.get("pos_label", "")),
    ):
        code = code.replace(token, value)
    (d / "code.py").write_text(code, encoding="utf-8")

    (d / "card.md").write_text(
        f"# {exp_id}  (parent: {parent} | kesif? hayir)\n"
        f"- Owner: {owner} | Kaggle notebook adi: {slug} | Kosu: hazirlaniyor\n"
        f"- Backlog maddesi: TODO (B-xx)\n"
        f"- Hipotez: {note}\n"
        f"- Dayanak: TODO (bu veride olculen gozlem)\n"
        f"- Degisiklik: TODO (parent'a gore tam olarak ne - diff.md'de satir satir)\n"
        f"- Mod/Seed/GPU: FULL / 42 / hayir\n"
        f"- Tahmini sure: TODO-TODO dk\n"
        f"- Sonuc: -\n"
        f"- Karar: -\n"
        f"- Atlanan dogrulama: -\n"
        f"- Codex incelemesi: yok\n"
        f"- Urun etkisi: -\n"
        f"- Ders: -\n",
        encoding="utf-8",
    )

    (d / "diff.md").write_text(
        f"# {exp_id} - parent {parent} farki\n\n"
        f"Insana kosudan ONCE gosterilen sey budur (CLAUDE.md: kod gorulmeden onay yok).\n\n"
        f"```diff\nTODO\n```\n",
        encoding="utf-8",
    )

    print(f"{exp_id} olusturuldu  ->  {d}")
    print(f"  owner={owner}  parent={parent}  Kaggle notebook adi: {slug}")
    print("  1. code.py'deki TODO'lari doldur (hazirla / model_kur)")
    print("  2. diff.md'yi doldur ve INSANA GOSTER - onaysiz kosu yok")
    print("  3. insan Kaggle'da kosturur, ekran ciktisini output/run_log.txt'ye koy")
    print(f"  4. `kx.py kayit {exp_id}`")


# -------------------------------------------------------------------- kayit

RESULT_RE = re.compile(r"=== KX RESULT JSON ===\s*(\{.*?\})\s*=== KX RESULT SONU ===", re.S)


def result_from_log(out: Path) -> dict | None:
    """Insanin yapistirdigi ekran ciktisindan result.json'i cikarir."""
    log = out / "run_log.txt"
    if not log.exists():
        return None
    m = RESULT_RE.search(log.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as exc:
        die(f"run_log.txt icindeki KX RESULT JSON blogu bozuk: {exc}")


def validate_submission(path: Path, cfg: dict, errs: list[str], atlanan: list[str]) -> None:
    """submission.csv'yi ornek dosyayla karsilastirir.

    Erken gonderim yapilmadigi icin format hatasini yakalayan TEK mekanizma budur.
    """
    import numpy as np

    ref_rel = cfg.get("sample_submission") or "data/sample_submission.csv"
    ref = ROOT / ref_rel
    if not ref.exists():
        atlanan.append(f"submission formati (referans {ref_rel} yok)")
        return
    try:
        sub, samp = _read_table(path), _read_table(ref)
    except Exception as exc:  # noqa: BLE001
        errs.append(f"submission.csv veya {ref_rel} okunamadi: {exc}")
        return

    if list(sub.columns) != list(samp.columns):
        errs.append(f"submission.csv kolonlari {list(sub.columns)}, beklenen {list(samp.columns)}")
        return
    if len(sub) != len(samp):
        errs.append(f"submission.csv {len(sub)} satir, beklenen {len(samp)}")
        return
    idc = samp.columns[0]
    if not sub[idc].equals(samp[idc]):
        if set(sub[idc]) == set(samp[idc]):
            errs.append(f"submission.csv: id kumesi dogru ama SIRA farkli ({idc})")
        else:
            eksik = len(set(samp[idc]) - set(sub[idc]))
            errs.append(f"submission.csv: id kumesi tutmuyor ({eksik} id eksik)")
        return
    for c in samp.columns[1:]:
        if sub[c].isna().any():
            errs.append(f"submission.csv: '{c}' kolonunda NaN var ({int(sub[c].isna().sum())} satir)")
            continue
        try:
            vals = sub[c].to_numpy(dtype="float64")
        except (TypeError, ValueError):
            continue  # sayisal olmayan hedef (etiket) - aralik kontrolu yok
        if not np.isfinite(vals).all():
            errs.append(f"submission.csv: '{c}' kolonunda inf var")


def validate_output(exp_id: str, out: Path, cfg: dict) -> tuple[list[str], list[str]]:
    """Cikti sozlesmesi (core/cv_spec.md). errs bossa sonuc kayda girebilir.

    Dosya indirilmediyse (yalniz ekran ciktisi yapistirildiysa) dosyaya bagli
    kontroller 'atlanan' listesine girer - sessizce gecilmez, card.md'ye yazilir.
    """
    errs: list[str] = []
    atlanan: list[str] = []
    result = read_result(exp_id)
    if result is None:
        return [f"result.json yok ve run_log.txt'den uretilemedi ({out})"], atlanan

    is_full = str(result.get("mode", "")).upper() == "FULL"

    expected_rows = expected_folds = None
    if FOLDS_PATH.exists():
        try:
            folds = _read_table(FOLDS_PATH)
            expected_rows = len(folds)
            if "fold" in folds.columns:
                expected_folds = int(folds["fold"].nunique())
        except Exception as exc:  # noqa: BLE001
            errs.append(f"core/folds.csv okunamadi: {exc}")
    else:
        atlanan.append("fold sayisi / satir hizalamasi (core/folds.csv yok)")

    # --- fold parmak izi: Kaggle'a dataset yuklemenin yerine gecen garanti
    fp_local = local_fingerprint()
    fp_run = result.get("fold_fingerprint")
    if fp_local is None:
        atlanan.append("fold parmak izi (yerel folds.csv veya folds_snippet.py yok)")
    elif not fp_run:
        errs.append("result.json: 'fold_fingerprint' yok - kosu fold sozlesmesini uygulamamis")
    elif fp_run != fp_local:
        errs.append(
            f"FOLD PARMAK IZI TUTMUYOR: kosu={fp_run} yerel={fp_local}. "
            "Kosu baska fold'larla egitilmis - sonuc onceki deneylerle karsilastirilamaz."
        )

    for name, need_rows in (("oof.parquet", True), ("test_preds.parquet", False)):
        path = out / name
        if not path.exists():
            atlanan.append(f"{name} kontrolu (dosya indirilmedi)")
            continue
        try:
            df = _read_table(path)
        except Exception as exc:  # noqa: BLE001
            errs.append(f"{name} okunamadi: {exc}")
            continue
        idc = "id" if "id" in df.columns else (cfg.get("id_col") or "id")
        if idc not in df.columns:
            errs.append(f"{name}: '{idc}' kolonu yok (kimliksiz tahmin yasak)")
            continue
        if df[idc].duplicated().any():
            errs.append(f"{name}: tekrar eden id var ({int(df[idc].duplicated().sum())} satir)")
        pred_cols = [c for c in df.columns if c not in (idc, "fold", "y")]
        if not pred_cols:
            errs.append(f"{name}: tahmin kolonu yok")
        elif df[pred_cols].isna().any().any():
            errs.append(f"{name}: tahmin kolonlarinda NaN var")
        if need_rows and is_full and expected_rows is not None and len(df) != expected_rows:
            errs.append(f"{name}: {len(df)} satir, folds.csv {expected_rows} satir - hizalama bozuk")

    sub_path = out / "submission.csv"
    if sub_path.exists():
        validate_submission(sub_path, cfg, errs, atlanan)
    else:
        atlanan.append("submission formati (submission.csv indirilmedi)")

    for field in ("exp_id", "cv_mean", "cv_oof", "fold_scores", "n_folds_done"):
        if field not in result:
            errs.append(f"result.json: '{field}' alani yok")

    # Skorlar sonlu olmali. Provada olculdu: roc_auc_score tek sinifli bir dilimde
    # hata vermez, NAN doner; kucuk FAST fold'lari bunu sessizce kayda sokabilir.
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
        errs.append(
            f"result.json n_folds_done={result.get('n_folds_done')}, beklenen {expected_folds} - FULL kosuda eksik fold"
        )
    if not result.get("mode"):
        errs.append("result.json: 'mode' alani yok (FAST/FULL ayrimi yapilamaz)")
    return errs, atlanan


def cmd_kayit(args, cfg) -> None:
    exp_id = normalize_exp(args.exp)
    d = exp_dir(exp_id)
    if not d.exists():
        die(f"{exp_id} klasoru yok. Once `kx.py new {exp_id}`.")
    out = d / "output"
    out.mkdir(exist_ok=True)

    if not (out / "result.json").exists():
        parsed = result_from_log(out)
        if parsed is None:
            die(
                f"{out}/result.json yok ve {out}/run_log.txt'de KX RESULT JSON blogu bulunamadi.\n"
                "  Insanin yapistirdigi ekran ciktisini run_log.txt'ye kaydet, sonra tekrar dene."
            )
        (out / "result.json").write_text(json.dumps(parsed, indent=2), encoding="utf-8")
        print(f"run_log.txt'den result.json uretildi ({out / 'result.json'})")

    errs, atlanan = validate_output(exp_id, out, cfg)
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
    append_line(
        SUMMARY_PATH,
        f"| {exp_id} | {result.get('owner', owner_of(exp_id))} | {result.get('parent', '-')} "
        f"| {result.get('mode', '-')} | {score} | {result.get('cv_mean')} | {result.get('cv_oof')} "
        f"| {len(folds)} | {result.get('runtime_min', '-')} | - "
        f"| {result.get('fold_fingerprint', '?')} |",
    )
    append_line(
        RUNS_PATH,
        f"| {slug_for(exp_id, cfg)} | {result.get('owner', owner_of(exp_id))} | {now()} "
        f"| {result.get('mode', '-')} | {result.get('runtime_min', '?')} | bitti |",
    )

    print(f"\nDOGRULAMA GECTI. {exp_id} ana skor ({main_key}): {score}")
    print(f"fold skorlari: {folds}")
    if atlanan:
        print("\nATLANAN DOGRULAMALAR (card.md'ye yaz, sessizce gecme):")
        for a in atlanan:
            print(f"  - {a}")
    print(f"\nEXP_SUMMARY.md + RUNS.md guncellendi. Siradaki: `kx.py cmp {exp_id}`")


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
        die(f"{exp_id} icin result.json yok. Once `kx.py kayit {exp_id}`.")

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
    cfp, pfp = child.get("fold_fingerprint"), parent.get("fold_fingerprint")
    if cfp and pfp and cfp != pfp:
        print(f"UYARI: fold parmak izleri farkli ({cfp} vs {pfp}). "
              "Iki kosu ayni fold'larda degil - fark modelden degil bolunmeden gelebilir.")

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
    co, po = child.get(other_key), parent.get(other_key)
    if co is not None and po is not None:
        other_diff = (co - po) * sign
        print(f"  ({other_key}: {exp_id}={co}  {parent_id}={po}  fark={other_diff:+.6f})")
        if main_diff != 0 and other_diff != 0 and (main_diff > 0) != (other_diff > 0):
            print(f"\n  UYARI: {key} ve {other_key} ZIT yone isaret ediyor "
                  f"({key} {'iyilesme' if main_diff > 0 else 'kotulesme'}, "
                  f"{other_key} {'iyilesme' if other_diff > 0 else 'kotulesme'}). "
                  "Otomatik oneri yalniz ana skora bakar - karari vermeden once ikisine de bak.")

    suggestion = "kanit yetersiz - fold skorlari eksik"
    if len(cf) == len(pf) and cf:
        diffs = [(c - p) * sign for c, p in zip(cf, pf)]
        sd, md = _std(diffs), _mean(diffs)
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
    print("  Karari insan verir. card.md'ye yaz, EXP_SUMMARY.md'deki Karar sutununu doldur,")
    print("  STATUS.md'yi guncelle.")


# -------------------------------------------------------------------- board

def cmd_board(args, cfg) -> None:
    print(f"=== KX BOARD  {datetime.now().strftime('%a %H:%M')} ===\n")

    print("-- Deneyler --")
    results = []
    bekleyen = []
    for d in sorted((ROOT / "experiments").glob("EXP-*")):
        r = read_result(d.name)
        if r:
            results.append((d.name, r))
        else:
            bekleyen.append(d.name)
    key = cfg.get("main_score", "cv_mean")
    gib = bool(cfg.get("greater_is_better", True))
    if not results:
        print("  (sonuclanmis deney yok)")
    else:
        for name, r in results[-10:]:
            print(f"  {name:9} {r.get('mode', '-'):5} {key}={r.get(key)}  ({r.get('owner', '-')})")
        scored = [(n, r) for n, r in results if isinstance(r.get(key), (int, float))]
        if scored:
            best = (max if gib else min)(scored, key=lambda t: t[1][key])
            print(f"\n  EN IYI ADAY: {best[0]}  {key}={best[1][key]}")
    if bekleyen:
        print(f"\n-- Sonucu bekleyen (kosuldu mu?) --\n  {', '.join(bekleyen)}")

    fp = local_fingerprint()
    print(f"\n-- Fold sozlesmesi --\n  yerel parmak izi: {fp or '(folds.csv yok - once D-01 + make_folds.py)'}")

    print("\n-- Hatirlatma --")
    print("  Kaggle'a hicbir sey gonderilmez. Kodu insan yapistirir, insan kosturur.")
    print("  Gonderim karari insanin. Oner; insan yaptiktan sonra log/SUBMISSIONS.md'ye yaz.")


# --------------------------------------------------------------------- main

def main() -> None:
    p = argparse.ArgumentParser(prog="kx", description="Deney dongusu. Kaggle'a gonderim yapmaz.")
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="deney klasoru + yapistirilacak code.py uret")
    n.add_argument("exp")
    n.add_argument("--parent")
    n.add_argument("--note")
    n.add_argument("--target")
    n.add_argument("--id-col", dest="id_col")
    n.add_argument("--pos-label", dest="pos_label")
    n.set_defaults(fn=cmd_new)

    k = sub.add_parser("kayit", help="yerel ciktiyi DOGRULA ve kaydet")
    k.add_argument("exp")
    k.set_defaults(fn=cmd_kayit)

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
