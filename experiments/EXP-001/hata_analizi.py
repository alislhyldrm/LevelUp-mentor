# EXP-001 — OOF hata analizi (Colab hücre 5 olarak koşuldu, 26 Eyl)
# Girdi: RUN_DIR/val_dets.json (EXP-001 val tahminleri) + D-01 val.json
# Amaç: sınıf başına AP'nin ayırmadığı şeyi ayırmak — kayıp KARIŞIKLIK mı, KAÇIRMA mı?
#
# YÖNTEM UYARISI: bu eşleştirme COCO'nun resmi eşleştirmesi DEĞİLDİR.
#   - açgözlü (GT sırasına göre, güvene göre değil)
#   - sınıf-BAĞIMSIZ (karışıklığı görebilmek için kasten; COCO sınıf içinde eşleştirir)
#   - tek skor eşiği (0,30); oranlar eşiğe duyarlıdır
# Yön güvenilir, ondalıklar yaklaşıktır. Skor olarak raporlanmaz, yalnız hipotez üretir.

import json, numpy as np
from collections import defaultdict
from pycocotools.coco import COCO

dets = json.load(open(f"{RUN_DIR}/val_dets.json"))
gt   = COCO(VAL_JSON)
ISIM = {0: "car", 1: "van", 2: "truck", 3: "bus"}
SKOR_ESIK = 0.30

def iou_mat(a, b):        # a,b: xywh
    if len(a) == 0 or len(b) == 0:
        return np.zeros((len(a), len(b)))
    a = np.array(a, dtype=float); b = np.array(b, dtype=float)
    ax1, ay1 = a[:, 0], a[:, 1]; ax2, ay2 = a[:, 0] + a[:, 2], a[:, 1] + a[:, 3]
    bx1, by1 = b[:, 0], b[:, 1]; bx2, by2 = b[:, 0] + b[:, 2], b[:, 1] + b[:, 3]
    ix1 = np.maximum(ax1[:, None], bx1[None]); iy1 = np.maximum(ay1[:, None], by1[None])
    ix2 = np.minimum(ax2[:, None], bx2[None]); iy2 = np.minimum(ay2[:, None], by2[None])
    inter = np.clip(ix2 - ix1, 0, None) * np.clip(iy2 - iy1, 0, None)
    ua = (a[:, 2] * a[:, 3])[:, None] + (b[:, 2] * b[:, 3])[None] - inter
    return inter / np.maximum(ua, 1e-9)

per_img = defaultdict(list)
for d in dets:
    if d["score"] >= SKOR_ESIK:
        per_img[d["image_id"]].append(d)

karisik = np.zeros((4, 5), dtype=int)          # [gt][0..3 tahmin sınıfı, 4 = KAÇIRILDI]
boyut_kacirma = defaultdict(lambda: [0, 0])    # gt sınıf -> [küçük kaçırma, küçük toplam]
for iid in gt.getImgIds():
    anns = gt.loadAnns(gt.getAnnIds(imgIds=[iid]))
    prs  = sorted(per_img.get(iid, []), key=lambda d: -d["score"])
    M = iou_mat([a["bbox"] for a in anns], [p["bbox"] for p in prs])
    kullanilan = set()
    for gi, a in enumerate(anns):
        gc = a["category_id"]; alan = a["bbox"][2] * a["bbox"][3]
        en_iyi, en_iyi_iou = -1, 0.5
        for pi in (np.argsort(-M[gi]) if len(prs) else []):
            if pi in kullanilan:
                continue
            if M[gi, pi] >= en_iyi_iou:
                en_iyi, en_iyi_iou = pi, M[gi, pi]
            break
        if en_iyi >= 0:
            kullanilan.add(en_iyi); karisik[gc][prs[en_iyi]["category_id"]] += 1
        else:
            karisik[gc][4] += 1
        if alan < 32 * 32:
            boyut_kacirma[gc][1] += 1
            if en_iyi < 0:
                boyut_kacirma[gc][0] += 1

print(f"KARISIKLIK MATRISI (IoU>=0.5, skor>={SKOR_ESIK}, sinif-bagimsiz eslestirme)")
print(f"{'GT\\tahmin':>10} {'car':>7} {'van':>7} {'truck':>7} {'bus':>7} {'KACIRILDI':>10} {'toplam':>8}")
for c in range(4):
    print(f"{ISIM[c]:>10} " + " ".join(f"{karisik[c][k]:>7}" for k in range(5)) + f" {karisik[c].sum():>8}")
print()
for c in range(4):
    t = karisik[c].sum(); dogru = karisik[c][c]; kacir = karisik[c][4]
    print(f"{ISIM[c]:>6}: dogru %{100*dogru/t:.1f} | YANLIS SINIF %{100*(t-dogru-kacir)/t:.1f}"
          f" | KACIRILDI %{100*kacir/t:.1f}   (n={t})")
print("\nKUCUK NESNE (<32^2) KACIRMA ORANI")
for c in range(4):
    k, t = boyut_kacirma[c]
    print(f"  {ISIM[c]:>6}: %{100*k/max(t,1):.1f} kacirildi  (kucuk gt n={t})")
