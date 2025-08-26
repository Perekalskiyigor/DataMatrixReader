# pip install opencv-python pylibdmtx zxing-cpp
# Если barcode-модуль в твоей сборке OpenCV отсутствует, блок с detector пропустится.
import cv2, numpy as np, sys, time

IMG_PATH = r"E:\DEV\DataMatrixReader\snapshot_2025-08-18_12-40-44_1.png"  # <-- замени на свой путь
# например: r"E:\DEV\DataMatrixReader\test.png"
# для этого чата примерный путь был: /mnt/data/snapshot_2025-08-18_12-40-44_1.png

def load_img(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Не смог открыть файл: {path}")
    return img

def upscale_for_dm(img, target_long=1400):
    h, w = img.shape[:2]
    scale = max(1.0, target_long / max(h, w))
    if scale == 1.0:
        return img, 1.0
    # NEAREST сохраняет края чёткими для штрихкодов
    out = cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_NEAREST)
    return out, scale

def preprocess_variants(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # контраст
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    g1 = clahe.apply(gray)

    # лёгкое подавление шума, сохранив края
    g2 = cv2.bilateralFilter(g1, 5, 50, 50)

    # разные бинаризации
    th1 = cv2.adaptiveThreshold(g2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 31, 10)
    th2 = cv2.adaptiveThreshold(g2, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                cv2.THRESH_BINARY, 31, 5)

    # иногда помогает инверсия (белый/чёрный перепутаны на сканах)
    inv1 = cv2.bitwise_not(th1)
    inv2 = cv2.bitwise_not(th2)

    # вернём список кандидатов
    return [
        img_bgr,                            # исходник
        cv2.cvtColor(g2, cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(th1, cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(th2, cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(inv1, cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(inv2, cv2.COLOR_GRAY2BGR),
    ]

def draw_poly(img, pts, color=(0,255,0), text=None):
    pts = np.asarray(pts, dtype=int).reshape(-1,2)
    cv2.polylines(img, [pts], True, color, 2)
    if text:
        cv2.putText(img, text, (pts[0][0], max(0, pts[0][1]-6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)

def try_opencv_barcode(img_bgr):
    found = []
    if not hasattr(cv2, "barcode_BarcodeDetector"):
        return found
    det = cv2.barcode_BarcodeDetector()
    # В некоторых сборках detect() + decode(), но тут попробуем «всё в одном»
    decoded_info, decoded_type, points = det.detectAndDecode(img_bgr)
    if decoded_info and points is not None:
        for data, dtype, pts in zip(decoded_info, decoded_type, points):
            if not data:
                continue
            found.append(("opencv", dtype, data, pts))
    return found

def try_pylibdmtx(img_bgr):
    try:
        from pylibdmtx.pylibdmtx import decode as dm_decode
    except Exception:
        return []
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    results = dm_decode(gray)
    out = []
    for r in results or []:
        data = r.data.decode("utf-8", errors="replace")
        x,y,w,h = r.rect.left, r.rect.top, r.rect.width, r.rect.height
        pts = np.array([[x,y],[x+w,y],[x+w,y+h],[x,y+h]], dtype=np.int32)
        out.append(("libdmtx", "DATAMATRIX", data, pts))
    return out

def try_zxingcpp(img_bgr):
    try:
        import zxingcpp
    except Exception:
        return []
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    results = zxingcpp.read_barcodes(gray, formats=zxingcpp.BarcodeFormat.DataMatrix)
    out = []
    for r in results:
        pts = [(p.x, p.y) for p in r.position]
        out.append(("zxing", "DATAMATRIX", r.text, np.array(pts, dtype=np.int32)))
    return out

def main():
    img0 = load_img(IMG_PATH)
    img, scale = upscale_for_dm(img0, target_long=1800)

    # Иногда скан чуть повернут — попробуем три поворота
    rotations = [0, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE]
    all_found = []

    for rot in rotations:
        test = cv2.rotate(img, rot) if rot != 0 else img.copy()
        for candidate in preprocess_variants(test):
            # 1) OpenCV barcode
            all_found += try_opencv_barcode(candidate)
            # 2) pylibdmtx
            all_found += try_pylibdmtx(candidate)
            # 3) zxing-cpp
            all_found += try_zxingcpp(candidate)

            if len(all_found) >= 1:
                # Можно снять break, если хочешь собрать максимум
                pass

    # Визуализация уникальных по payload
    vis = img.copy()
    seen = set()
    for src, dtype, data, pts in all_found:
        if data in seen:
            continue
        seen.add(data)
        draw_poly(vis, pts, text=data)

    print(f"Найдено уникальных кодов: {len(seen)}")
    if len(seen) == 0:
        print("Советы: усилить резкость/контраст, увеличить скан до 150–200 dpi/мм кода, "
              "следить за 'тихой зоной' вокруг меток и попробовать zxing-cpp.")
    cv2.imshow("Detected DataMatrix", vis)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
