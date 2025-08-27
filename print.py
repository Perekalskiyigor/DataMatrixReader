import subprocess
import os
import shutil
from pathlib import Path

def print_png_via_mspaint(image_path: str, printer_name: str):
    """
    Печатает PNG (или другое изображение) через MSPaint без диалога.

    :param image_path: путь к изображению
    :param printer_name: имя очереди принтера (UNC или локальное)
    """
    if not Path(image_path).is_file():
        raise FileNotFoundError(image_path)

    mspaint = shutil.which("mspaint.exe") or r"C:\Windows\System32\mspaint.exe"

    result = subprocess.run([mspaint, "/pt", image_path, printer_name])
    if result.returncode != 0:
        raise RuntimeError(f"MSPaint вернул код {result.returncode}")

    print("Изображение отправлено на печать через MSPaint (/pt).")
