# EXP-001 — D-FINE-S baseline, SIFIRDAN eğitim (Colab T4, Colab MCP ile koşulur)
# Backlog: — (ilk baseline, keşif değil)
# Hipotez: 960 girişte sıfırdan eğitilmiş D-FINE-S, bu veride ölçülebilir bir mAP@0.5 zemini verir
# Dayanak: EDA — kutuların %38'i <32², 640'ta p5 kenar ≈ 7 px (case/CASE.md satır 6)
# Süre: ÖLÇÜLDÜ (smoke, T4). Eğitim 0,912 sn/adım, val 0,538 sn/adım @ batch 8, 960.
#   → tam koşu 9,8 dk eğitim + 1,5 dk val = 11,3 dk/epoch; 60 epoch ≈ 11,3 sa. Bellek 6,9/15,4 GB.
#
# TEKNIKLER
# - D-FINE-S / HGNetv2-B0, **sıfırdan** (rastgele başlatma) · neden: D-03 dış veri yasağı, D-05
#   Objects365 ağırlığı yasak · sızıntı: yok — hiçbir dış ağırlık yüklenmiyor.
#   DİKKAT: repo varsayılanı `HGNetv2.pretrained: True` (configs/dfine/include/dfine_hgnetv2.yml);
#   açıkça False yapılmazsa ImageNet ağırlığı sessizce iner. Aşağıda kapatılıyor ve DOĞRULA'da basılıyor.
# - Giriş 960x960, yapılandırılmış override ile (regex değil) · neden: küçük nesne · sızıntı: yok
# - Multiscale KAPALI (`base_size_repeat: null`) · neden: 960 tabanda ölçek üretimi 960'ın belirgin
#   üstüne çıkar, T4 15,6 GB'ta OOM riski; ayrıca baseline tek değişkenli kalsın · sızıntı: yok
# - Augmentasyon repo varsayılanı (zoom-out + IoU-crop dahil) · neden: baseline sade kalsın;
#   "zoom-out küçük nesneye zarar veriyor" bir HİPOTEZ, backlog maddesi, baseline'a gömülmez
# - LR: repo S tarifinin (batch 64, lr 4e-4) sqrt ölçeklemesi ile batch 8'e indirgenmesi · ÖLÇÜLMEDİ
# - Val = D-01 sabit bölmesi (%20 stratified, seed 42); parmak izi zorunlu karşılaştırılır
# - AMP (fp16) · neden: T4 bellek/hız · sızıntı: yok
# - Skor: **geçici yerel AP50** — COCO, maxDets=300. Resmi scorer'ın interpolasyonu, tespit sınırı
#   ve "200 px² altı puanı etkilemez" kuralının nasıl işlendiği bilinmiyor (CASE.md satır 2).
#   maxDets=300 gerekçesi: COCO'nun 100 sınırı görüntü×SINIF başına uygulanır ve val'de
#   7 görüntü–sınıf çifti 100'ü aşıyor (max 132) — ölçüldü.
#
# Hücreler "# %%" ile ayrılır: 1 kurulum · 2 eğitimi başlat/sürdür · 3 durum+süre · 4 değerlendirme.

# %% [1] KURULUM ------------------------------------------------------------------------------
import os, sys, json, glob, time, random, hashlib, shutil, subprocess, zipfile
from pathlib import Path

EXP       = "EXP-001"
SEED      = 0
MODEL     = "s"          # n / s / m / l / x  — sıfırdan eğitimde küçük model tercih edildi
IMG       = 960          # giriş çözünürlüğü (kare)
EPOCHS    = 60           # SMOKE ölçümünden sonra kesinleşir
SMOKE     = False        # True: 256 train / 128 val görüntü, 2 epoch — boru hattı testi
PRETRAINED_BACKBONE = False   # D-05: Objects365 YASAK. ImageNet backbone de dış ağırlıktır → False.

DRIVE_ZIP = "/content/drive/MyDrive/dfine_data.zip"
RUN_DIR   = f"/content/drive/MyDrive/dfine_runs/{EXP}{'_smoke' if SMOKE else ''}"
DATA      = "/content/dfine_data"
REPO      = "/content/D-FINE"
REPO_PIN  = "956d1709314c2c6a4df6f34de232054578a7449f"   # incelenen revizyon

def sh(cmd, check=True):
    print("$", cmd)
    return subprocess.run(cmd, shell=True, check=check)

from google.colab import drive
drive.mount("/content/drive")
Path(RUN_DIR).mkdir(parents=True, exist_ok=True)

import torch
assert torch.cuda.is_available(), "GPU yok: Runtime > Change runtime type > GPU"
gpu = torch.cuda.get_device_properties(0)
GPU_GB = gpu.total_memory / 1e9
print(f"GPU: {gpu.name} {GPU_GB:.1f} GB | torch {torch.__version__} | CPU {os.cpu_count()}")

# --- Veri: Drive'dan yerel diske (Drive'dan tek tek okumak epoch başına dakikalar kaybettirir) ---
if not Path(DATA, "images").exists():
    t = time.time()
    shutil.copy(DRIVE_ZIP, "/content/d.zip")
    zipfile.ZipFile("/content/d.zip").extractall("/content")
    os.remove("/content/d.zip")
    print(f"veri açıldı: {time.time()-t:.0f} sn")
print("görsel:", len(os.listdir(f"{DATA}/images")))

TRAIN_JSON, VAL_JSON = f"{DATA}/annotations/train.json", f"{DATA}/annotations/val.json"

# --- Bölme parmak izi (K-06'nın tespit karşılığı) -------------------------------------------
# Dataset yüklenmediği için garanti dosya paylaşımı değil, içerik özetinin eşitliğidir.
# Beklenen değerler yereldeki data/split/{train,val}.json'dan hesaplandı (D-01, seed 42).
BEKLENEN = {
    "train": {"images": 5175, "boxes": 132989},
    "val":   {"images": 1294, "boxes":  32343},
}
def parmak_izi(p):
    d = json.load(open(p))
    adlar = sorted(i["file_name"] for i in d["images"])
    h = hashlib.sha256("\n".join(adlar).encode()).hexdigest()[:16]
    sayim = {}
    for a in d["annotations"]:
        sayim[a["category_id"]] = sayim.get(a["category_id"], 0) + 1
    return d, {"images": len(d["images"]), "boxes": len(d["annotations"]), "sha16": h,
               "sinif": {k: sayim.get(k, 0) for k in range(4)},
               "kategoriler": [(c["id"], c["name"]) for c in sorted(d["categories"], key=lambda c: c["id"])]}

FP = {}
for ad, p in (("train", TRAIN_JSON), ("val", VAL_JSON)):
    d, fp = parmak_izi(p); FP[ad] = fp
    print(f"PARMAK İZİ {ad}: {fp}")
    assert fp["images"] == BEKLENEN[ad]["images"], f"{ad} görüntü sayısı tutmuyor: {fp['images']} != {BEKLENEN[ad]['images']}"
    assert fp["boxes"]  == BEKLENEN[ad]["boxes"],  f"{ad} kutu sayısı tutmuyor: {fp['boxes']} != {BEKLENEN[ad]['boxes']}"
    assert fp["kategoriler"] == [(0, "car"), (1, "van"), (2, "truck"), (3, "bus")], fp["kategoriler"]
# train/val görüntü kesişimi sıfır olmalı (D-01)
_tr = {i["file_name"] for i in json.load(open(TRAIN_JSON))["images"]}
_va = {i["file_name"] for i in json.load(open(VAL_JSON))["images"]}
assert not (_tr & _va), f"train/val kesişimi var: {len(_tr & _va)} görüntü — SIZINTI"
print("bölme doğrulandı: kesişim 0")

# --- SMOKE alt kümesi: ilk N değil, sınıf varlığını gözeten sabit seed'li örnek --------------
if SMOKE:
    def alt_kume(src, n):
        d = json.load(open(src))
        per = {}
        for a in d["annotations"]:
            per.setdefault(a["image_id"], set()).add(a["category_id"])
        rng = random.Random(42)
        secili, kalan = [], [i["id"] for i in d["images"]]
        rng.shuffle(kalan)
        # önce her sınıftan en az 5 görüntü garanti et (bus %3,4 — rastgelede düşebilir)
        for c in range(4):
            aday = [i for i in kalan if c in per.get(i, set())][:5]
            secili += [i for i in aday if i not in secili]
        for i in kalan:
            if len(secili) >= n: break
            if i not in secili: secili.append(i)
        ids = set(secili[:n])
        d["images"]      = [i for i in d["images"] if i["id"] in ids]
        d["annotations"] = [a for a in d["annotations"] if a["image_id"] in ids]
        out = src.replace(".json", "_smoke.json"); json.dump(d, open(out, "w"))
        dag = {}
        for a in d["annotations"]: dag[a["category_id"]] = dag.get(a["category_id"], 0) + 1
        print(f"SMOKE {Path(out).name}: {len(d['images'])} görüntü, sınıf dağılımı {dag}")
        assert all(dag.get(c, 0) > 0 for c in range(4)), "SMOKE alt kümesinde eksik sınıf var"
        return out
    TRAIN_JSON, VAL_JSON = alt_kume(TRAIN_JSON, 256), alt_kume(VAL_JSON, 128)

# --- Repo: sabit revizyon + bağımlılık -------------------------------------------------------
if not Path(REPO).exists():
    sh(f"git clone -q https://github.com/Peterande/D-FINE.git {REPO}")
    sh(f"git -C {REPO} checkout -q {REPO_PIN}")
    sh(f"pip install -q -r {REPO}/requirements.txt")
REPO_REV = subprocess.check_output(f"git -C {REPO} rev-parse HEAD", shell=True, text=True).strip()
assert REPO_REV == REPO_PIN, f"repo revizyonu incelenen sürüm değil: {REPO_REV}"
import importlib.util
assert importlib.util.find_spec("pycocotools"), "pycocotools yok — değerlendirme çalışmaz"
print("repo", REPO_REV[:8], "| pycocotools OK")

# --- Config ---------------------------------------------------------------------------------
import yaml
# (a) veri yolu + sınıf sayısı. Kategori id'leri 0-3 → remap kapalı, num_classes=4
ds_path = f"{REPO}/configs/dataset/custom_detection.yml"
ds = yaml.safe_load(open(ds_path))
ds["num_classes"] = 4
ds["remap_mscoco_category"] = False
ds["train_dataloader"]["dataset"].update(img_folder=f"{DATA}/images", ann_file=TRAIN_JSON)
ds["val_dataloader"]["dataset"].update(img_folder=f"{DATA}/images", ann_file=VAL_JSON)
yaml.safe_dump(ds, open(ds_path, "w"), sort_keys=False)

# (b) SIFIRDAN eğitim config'i (obj2custom DEĞİL — o Objects365 fine-tune hattıdır)
base_cfg = f"{REPO}/configs/dfine/custom/dfine_hgnetv2_{MODEL}_custom.yml"
assert Path(base_cfg).exists(), f"config yok: {base_cfg}"

E      = 2 if SMOKE else EPOCHS
NO_AUG = 1 if SMOKE else max(4, E // 8)     # son NO_AUG epoch'ta güçlü augmentasyon kapanır
# Batch: ölçülen bellekten türetildi. T4'te batch 8 = 7,28 GB zirve → sabit maliyet ~1,5 GB,
# örnek başına ~0,72 GB. A100 40 GB'ta batch 32 ≈ 24,5 GB (15 GB pay), L4 22 GB'ta batch 16 ≈ 13 GB.
# A100'de daha da büyük batch sığar ama epoch süresi batch'e değil görüntü sayısına bağlı;
# batch küçük tutmak epoch'u yavaşlatmadan optimizer adım sayısını artırır. 5175 görüntülük
# sıfırdan eğitimde adım sayısı değerli, o yüzden A100'de 64 değil 32.
if   GPU_GB > 35: BATCH = 32      # A100 40/80 GB → ≈24,5 GB
elif GPU_GB > 20: BATCH = 16      # L4 22 GB      → ≈13 GB
elif GPU_GB > 14: BATCH = 8       # T4 15,6 GB (ölçüldü: 7,28 GB zirve)
else:             BATCH = 4
WORKERS = max(2, min(8, os.cpu_count()))   # T4 runtime 2 vCPU verir; L4/A100 daha fazlasını
# LR: repo S tarifi batch 64'te lr 4e-4 / backbone 2e-4. sqrt ölçekleme ile batch BATCH'e indir.
# ÖLÇÜLMEDİ — sıfırdan eğitimde doğru LR bu veride sınanmadı.
ADIM_EP = 5175 // BATCH
# warmup ITERASYON cinsinden (src/solver/det_engine.py:119, eğitim döngüsü içinde adımlanıyor)
# ve lr_scheduler warmup bitene kadar hiç adımlamıyor (det_solver.py:94). Sabit 1000 yazılırsa
# batch büyüdükçe warmup epoch cinsinden uzar: batch 48'de 1000 iter = 9,3 epoch. Adıma bağla.
WARMUP  = 50 if SMOKE else max(100, 2 * ADIM_EP)
ol      = (BATCH / 64) ** 0.5
LR      = round(4e-4 * ol, 7)
LR_BB   = round(2e-4 * ol, 7)

# 960 çözünürlüğü ÜÇ yerde de yapılandırılmış override ile ver (regex yok):
#   eval_spatial_size · train Resize.size · val Resize.size · collate_fn.base_size
TRAIN_OPS = [
    {"type": "RandomPhotometricDistort", "p": 0.5},
    {"type": "RandomZoomOut", "fill": 0},
    {"type": "RandomIoUCrop", "p": 0.8},
    {"type": "SanitizeBoundingBoxes", "min_size": 1},
    {"type": "RandomHorizontalFlip"},
    {"type": "Resize", "size": [IMG, IMG]},
    {"type": "SanitizeBoundingBoxes", "min_size": 1},
    {"type": "ConvertPILImage", "dtype": "float32", "scale": True},
    {"type": "ConvertBoxes", "fmt": "cxcywh", "normalize": True},
]
VAL_OPS = [
    {"type": "Resize", "size": [IMG, IMG]},
    {"type": "ConvertPILImage", "dtype": "float32", "scale": True},
]
exp_cfg = {
    "__include__": [base_cfg],
    "output_dir": RUN_DIR,
    "epochs": E,                       # DİKKAT: repo `epochs` okur. `epoches` yazılırsa sessizce
                                       # config varsayılanı (S için 220) koşar — taslaktaki hata buydu.
    "seed": SEED,
    "eval_spatial_size": [IMG, IMG],
    "checkpoint_freq": 1,              # her epoch last.pth → oturum koparsa Drive'dan devam
    "HGNetv2": {
        "pretrained": PRETRAINED_BACKBONE,   # D-05: dış ağırlık yok
        "freeze_at": -1, "freeze_norm": False,
    },
    "train_dataloader": {
        "total_batch_size": BATCH, "num_workers": WORKERS,
        "dataset": {"transforms": {"ops": TRAIN_OPS,
                                   "policy": {"name": "stop_epoch", "epoch": E - NO_AUG,
                                              "ops": ["RandomPhotometricDistort", "RandomZoomOut", "RandomIoUCrop"]}}},
        "collate_fn": {"base_size": IMG,
                       "base_size_repeat": None,   # multiscale KAPALI (scales=None) — T4 OOM koruması
                       "stop_epoch": E - NO_AUG},
    },
    "val_dataloader": {
        "total_batch_size": BATCH, "num_workers": WORKERS,
        "dataset": {"transforms": {"ops": VAL_OPS}},
    },
    "optimizer": {
        "type": "AdamW", "lr": LR, "betas": [0.9, 0.999], "weight_decay": 1.25e-4,
        "params": [
            {"params": "^(?=.*backbone)(?!.*norm|bn).*$", "lr": LR_BB},
            {"params": "^(?=.*backbone)(?=.*norm|bn).*$", "lr": LR_BB, "weight_decay": 0.0},
            {"params": "^(?=.*(?:encoder|decoder))(?=.*(?:norm|bn|bias)).*$", "weight_decay": 0.0},
        ],
    },
    "lr_scheduler": {"type": "MultiStepLR", "milestones": [max(1, int(E * 0.85))], "gamma": 0.1},
    "lr_warmup_scheduler": {"type": "LinearWarmup", "warmup_duration": WARMUP},
}
CFG = f"{REPO}/configs/dfine/custom/{EXP.lower()}.yml"
yaml.safe_dump(exp_cfg, open(CFG, "w"), sort_keys=False, default_flow_style=False)
print(f"config: {CFG}\n  epoch {E} (son {NO_AUG} epoch aug kapalı) | batch {BATCH} | workers {WORKERS}"
      f" | lr {LR} (backbone {LR_BB}) | adım/epoch {ADIM_EP} | warmup {WARMUP} iter")

# --- Çözülmüş config'ten kritik değerleri DOĞRULA (yanlış patch sessiz geçmesin) -------------
sys.path.insert(0, REPO); os.chdir(REPO)
from src.core import YAMLConfig
_c  = YAMLConfig(CFG).yaml_cfg
_tr = _c["train_dataloader"]; _va = _c["val_dataloader"]
_rs = [o for o in _tr["dataset"]["transforms"]["ops"] if o["type"] == "Resize"]
_vs = [o for o in _va["dataset"]["transforms"]["ops"] if o["type"] == "Resize"]
print("\nDOĞRULA",
      "| num_classes", _c["num_classes"],
      "| epochs", _c["epochs"],
      "| eval_spatial_size", _c["eval_spatial_size"],
      "| base_size", _tr["collate_fn"].get("base_size"),
      "| base_size_repeat", _tr["collate_fn"].get("base_size_repeat"),
      "| train_resize", _rs, "| val_resize", _vs,
      "| HGNetv2.pretrained", _c["HGNetv2"]["pretrained"],
      "| lr", _c["optimizer"]["lr"],
      "| ann", Path(_tr["dataset"]["ann_file"]).name)
assert _c["num_classes"] == 4
assert _c["epochs"] == E, f"epochs override tutmadı: {_c['epochs']} != {E}"
assert _c["eval_spatial_size"] == [IMG, IMG]
assert _tr["collate_fn"]["base_size"] == IMG
assert _tr["collate_fn"]["base_size_repeat"] is None, "multiscale kapanmadı — T4'te OOM riski"
assert _rs and _rs[0]["size"] == [IMG, IMG] and _vs and _vs[0]["size"] == [IMG, IMG]
assert _c["HGNetv2"]["pretrained"] is False, "DIŞ AĞIRLIK AÇIK — D-03/D-05 ihlali"
assert _tr["total_batch_size"] == BATCH
print("DOĞRULA: tüm kontroller geçti")

# %% [2] EĞİTİMİ BAŞLAT / SÜRDÜR (arka planda; hücre hemen döner) --------------------------------
# Sıfırdan eğitim: -t (tuning) YOK. Yalnız kopmuş koşuda -r ile last.pth'ten devam edilir.
# NOT: desen "[t]rain.py" — duz 'train.py -c' pgrep'in KENDI kabugunu eslestirir ve
#      kosu yokken bile CALISIYOR der (taslaktaki sessiz hata, smoke'ta yakalandi).
PGREP = "pgrep -f '[t]rain.py -c'"
calisiyor = subprocess.run(PGREP, shell=True, capture_output=True).returncode == 0
assert not calisiyor, "zaten koşan bir eğitim var — iki koşu aynı RUN_DIR'e yazar, durduruldu"
last = Path(RUN_DIR, "last.pth")
init = f"-r {last}" if last.exists() else ""          # ön-eğitimli ağırlık yok
cmd = (f"cd {REPO} && nohup torchrun --master_port=7777 --nproc_per_node=1 train.py "
       f"-c {CFG} --use-amp --seed={SEED} {init} >> {RUN_DIR}/train_log.txt 2>&1 &")
print("başlıyor:", "DEVAM (last.pth)" if last.exists() else "SIFIRDAN (rastgele başlatma)")
Path(RUN_DIR, "basladi.txt").write_text(str(time.time()))
subprocess.Popen(cmd, shell=True, start_new_session=True)

# %% [3] DURUM + SÜRE TAHMİNİ ------------------------------------------------------------------
def durum(tail=12):
    satir = []
    lp = Path(RUN_DIR, "log.txt")
    if lp.exists():
        for line in open(lp):
            try:
                r = json.loads(line)
                ap = r.get("test_coco_eval_bbox") or [None] * 2
                satir.append((r.get("epoch"), ap[0], ap[1]))
            except Exception:
                pass
    for ep, ap, ap50 in satir[-8:]:
        print(f"  epoch {ep:>3} | AP50:95 {ap:.4f} | AP50 {ap50:.4f}   (repo içi, maxDets=100)")
    t0 = float(Path(RUN_DIR, "basladi.txt").read_text())
    gecen = time.time() - t0
    n = len(satir)
    if n:
        sn_ep = gecen / n
        print(f"\nSÜRE: {n}/{E} epoch, {gecen/60:.1f} dk geçti → epoch başına {sn_ep/60:.1f} dk")
        print(f"  {E} epoch tahmini TOPLAM: {sn_ep*E/3600:.1f} sa (kalan {sn_ep*(E-n)/3600:.1f} sa)")
        if SMOKE:
            oran = 5175 / 256
            print(f"  → TAM koşu (5175 görüntü) epoch başına ≈ {sn_ep*oran/60:.1f} dk;"
                  f" 60 epoch ≈ {sn_ep*oran*60/3600:.1f} sa (kaba, val maliyeti farklı ölçeklenir)")
    else:
        print(f"\nSÜRE: henüz epoch bitmedi, {gecen/60:.1f} dk geçti")
    kosuyor = subprocess.run("pgrep -f '[t]rain.py -c'", shell=True, capture_output=True).returncode == 0
    print("süreç:", "ÇALIŞIYOR" if kosuyor else "DURDU")
    print(subprocess.run(f"tail -n {tail} {RUN_DIR}/train_log.txt", shell=True,
                         capture_output=True, text=True).stdout[-2500:])
    return kosuyor, satir

durum()

# %% [4] DEĞERLENDİRME: geçici yerel AP50 (maxDets=300) + sınıf başına AP50 --------------------
import numpy as np, torchvision.transforms as T
from PIL import Image
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

kosuyor, satir = durum(1)
assert not kosuyor, "eğitim hâlâ koşuyor — kısmi checkpoint tam koşu gibi raporlanmasın"
BITEN_EPOCH = len(satir)
if BITEN_EPOCH < E:
    print(f"UYARI: {BITEN_EPOCH}/{E} epoch bitti. Sonuç TAM koşu değildir, kayda böyle geçer.")

ckpt = next(p for p in (Path(RUN_DIR, n) for n in ("best_stg2.pth", "best_stg1.pth", "last.pth")) if p.exists())
sd = torch.load(ckpt, map_location="cpu")
CKPT_EPOCH = sd.get("last_epoch", "bilinmiyor")
print(f"checkpoint: {ckpt.name} (epoch {CKPT_EPOCH}) | biten epoch: {BITEN_EPOCH}/{E}")
# NOT: repo en iyi checkpoint'i AP50:95'e göre seçer (src/solver/det_solver.py), ana skorumuz AP50.
#      En iyi AP50 epoch'u ile çakışmayabilir — "riskli ama ölçülebilir", card.md'ye yazılır.

cfg = YAMLConfig(CFG, resume=str(ckpt))
cfg.yaml_cfg["HGNetv2"]["pretrained"] = False     # değerlendirmede de dış ağırlık inmesin
cfg.model.load_state_dict(sd["ema"]["module"] if "ema" in sd else sd["model"])
model, post = cfg.model.deploy().cuda().eval(), cfg.postprocessor.deploy()

gt  = COCO(VAL_JSON)
tf  = T.Compose([T.Resize((IMG, IMG)), T.ToTensor()])
ids = gt.getImgIds()
dets, BS = [], BATCH
with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16):
    for i in range(0, len(ids), BS):
        infos = gt.loadImgs(ids[i:i + BS])
        ims   = [Image.open(f"{DATA}/images/{m['file_name']}").convert("RGB") for m in infos]
        x     = torch.stack([tf(im) for im in ims]).cuda()
        sizes = torch.tensor([[m["width"], m["height"]] for m in infos]).cuda()
        labels, boxes, scores = post(model(x), sizes)
        for m, l, b, s in zip(infos, labels, boxes, scores):
            b = b.float().cpu().numpy(); b[:, 2:] -= b[:, :2]      # xyxy → xywh, orijinal piksel
            for lk, bk, sk in zip(l.cpu().tolist(), b.tolist(), s.float().cpu().tolist()):
                dets.append({"image_id": m["id"], "category_id": int(lk), "bbox": bk, "score": float(sk)})
print("tahmin:", len(dets), "kutu,", len(ids), "görüntü")
assert dets, "hiç tahmin yok — loadRes boş listede çöker; koşu başarısız sayılır"
# D-00 ölçümü: 200 px² altı tahmin oranı (baseline'da FİLTRELENMİYOR, yalnız ölçülüyor)
kucuk = sum(1 for d in dets if d["bbox"][2] * d["bbox"][3] < 200)
print(f"200 px² altı tahmin: {kucuk} ({100*kucuk/len(dets):.1f}%) — filtrelenmedi, D-00 backlog ölçümü")

def degerlendir(max_det):
    ev = COCOeval(gt, gt.loadRes(dets), "bbox")
    ev.params.maxDets = [1, 10, max_det]
    ev.evaluate(); ev.accumulate()
    p   = ev.eval["precision"]                    # [iou, recall, cat, area, maxDet]
    p50 = p[0, :, :, 0, -1]                       # IoU=0.5, alan=all, maxDets[-1]
    per = {gt.cats[c]["name"]: float(p50[:, k][p50[:, k] > -1].mean())
           for k, c in enumerate(ev.params.catIds)}
    ap50 = float(np.mean(list(per.values())))
    q    = p[:, :, :, 0, -1]                      # AP50:95 — stats[0] maxDets=100 arar, -1 döner
    ap5095 = float(q[q > -1].mean())
    return ap50, ap5095, per

ap50_300, ap5095_300, per_cls = degerlendir(300)
ap50_100, _, _                = degerlendir(100)
for c in range(4):
    assert gt.getAnnIds(catIds=[c]), f"val'de sınıf {c} GT'si yok — AP tanımsız"

print("\n=== KX RESULT JSON ===")
print(json.dumps({
    "exp": EXP, "main_score": round(ap50_300, 5),
    "metric": "gecici yerel AP50 (COCO, maxDets=300, 4 sinif ortalamasi)",
    "ap50_maxdet100": round(ap50_100, 5), "ap_50_95": round(ap5095_300, 5),
    "per_class_ap50": {k: round(v, 4) for k, v in per_cls.items()},
    "model": f"dfine_{MODEL}_scratch", "pretrained_backbone": PRETRAINED_BACKBONE,
    "img": IMG, "epochs_planned": E, "epochs_done": BITEN_EPOCH, "ckpt_epoch": CKPT_EPOCH,
    "batch": BATCH, "lr": LR, "lr_backbone": LR_BB, "seed": SEED,
    "gpu": gpu.name, "ckpt": ckpt.name, "repo_rev": REPO_REV[:8], "smoke": SMOKE,
    "val_images": len(ids), "n_dets": len(dets), "dets_under_200px2": kucuk,
    "split": "D-01 seed42 %20 stratified", "fingerprint": {k: FP[k]["sha16"] for k in FP},
}, ensure_ascii=False, indent=1))
print("=== END KX RESULT ===")
json.dump(dets, open(f"{RUN_DIR}/val_dets.json", "w"))
print("tahminler kaydedildi:", f"{RUN_DIR}/val_dets.json")
