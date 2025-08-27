from typing import List
import cv2
from PIL import Image, ImageOps
from pylibdmtx.pylibdmtx import decode, encode

def process_datamatrix_fast(
    image_path: str,
    output_path: str = "result_dm.png",
    max_dim: int = 1200,
    timeout_ms: int = 500,      # ограничим время распознавания
    max_count: int = 256,       # максим. число кодов, которое ищем
    scale: int = 8,             # масштаб модулей у итогового DM
    border_modules: int = 4     # рамка (в модулях)
) -> str:
    """
    1) Быстро распознаёт все DataMatrix на изображении.
    2) Склеивает содержимое через запятую.
    3) Генерирует единый DataMatrix и сохраняет в output_path.
    Возвращает output_path.
    """
    # --- быстрый препроцесс (ускоряет decode) ---
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Не удалось открыть файл: {image_path}")

    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        s = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Пробуем нормальный и инвертированный варианты — но оба с таймаутом.
    def _decode_np(a):
        # pylibdmtx принимает numpy-изображение
        return decode(a, max_count=max_count, timeout=timeout_ms) or []

    decoded = _decode_np(gray)
    if not decoded:
        inv = cv2.bitwise_not(gray)
        decoded = _decode_np(inv)

    texts: List[str] = [d.data.decode("utf-8", errors="replace") for d in decoded]
    if not texts:
        raise ValueError("DataMatrix-коды не найдены (или истёк таймаут).")

    combined = ",".join(texts)

    # --- генерация итогового DataMatrix (быстро) ---
    enc = encode(combined.encode("utf-8"))
    dm = Image.frombytes("RGB", (enc.width, enc.height), enc.pixels).convert("1")
    dm = dm.resize((dm.width * scale, dm.height * scale), Image.NEAREST)
    dm = ImageOps.expand(dm, border=border_modules * scale, fill="white")
    dm.save(output_path)
    return output_path



out = process_datamatrix_fast(r"e:\DEV\DataMatrixReader\snapshot_2025-08-26_08-36-38_1.png",
                         r"e:\DEV\DataMatrixReader\final_dm.png")
print("Итоговый DataMatrix сохранён в:", out)