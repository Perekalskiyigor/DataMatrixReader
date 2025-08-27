import os
import tkinter as tk
from tkinter import messagebox
import cv2
from pylibdmtx.pylibdmtx import decode, encode
from PIL import Image, ImageTk, ImageOps
import numpy as np
import cam
import print

printer_name = r"\\sis006179\Godex RT230"
image_path = r"e:\DEV\DataMatrixReader\big_dm.png"

# Глобальное хранилище считанных данных
decoded_data = []

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return None

    # Уменьшение до максимального размера 1000px
    max_dim = 1000
    h, w = image.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        image = cv2.resize(image, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)

    # Обрезка лишнего фона
    image = crop_image(image)

    # Серое изображение
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    final_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    return final_image

def crop_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        all_points = np.vstack(contours)
        x, y, w, h = cv2.boundingRect(all_points)
        return image[y:y+h, x:x+w]
    return image

def read_datamatrix_whole_image(image_path):
    image = preprocess_image(image_path)

    if image is None:
        messagebox.showerror("Ошибка", f"Не удалось открыть изображение:\n{image_path}")
        return []

    decoded_objects = decode(image)

    if not decoded_objects:
        messagebox.showwarning("Внимание", "⚠️ DataMatrix-коды не найдены на изображении.")
        return []

    results = []
    for obj in decoded_objects:
        data = obj.data.decode('utf-8', errors='replace')
        results.append(data)

    return results

def generate_big_datamatrix(data_list, output_path="big_dm.png", module_scale=10, border_modules=4):
    """
    Генерирует один DataMatrix, содержащий объединённые данные (через запятую),
    масштабирует модули (пиксели) для печати и добавляет белую рамку.
    """
    if not data_list:
        raise ValueError("data_list пуст.")

    combined_data = ",".join(data_list)

    # Кодирование DataMatrix
    enc = encode(combined_data.encode("utf-8"))
    # Преобразование в PIL.Image
    img = Image.frombytes('RGB', (enc.width, enc.height), enc.pixels)

    # ЧБ (на всякий) и масштабирование "модулей" без сглаживания
    img = img.convert("1")
    w, h = img.size
    img = img.resize((w * module_scale, h * module_scale), resample=Image.NEAREST)

    # Белая рамка (в модулях)
    border_px = border_modules * module_scale
    img = ImageOps.expand(img, border=border_px, fill="white")

    img.save(output_path)
    return output_path

def on_select_image():
    image_path_local = cam.capture_image()
    global decoded_data
    file_path = image_path_local
    if not file_path:
        return

    decoded_data = read_datamatrix_whole_image(file_path)

    text_box.delete("1.0", tk.END)
    for i, item in enumerate(decoded_data, 1):
        text_box.insert(tk.END, f"{i:02d}: {item}\n")

def on_generate_dm():
    if not decoded_data:
        messagebox.showwarning("Ошибка", "Нет считанных данных для DataMatrix.")
        return
    try:
        out_path = generate_big_datamatrix(decoded_data, output_path=image_path, module_scale=10, border_modules=4)
        print.print_png_via_mspaint(out_path, printer_name)
        messagebox.showinfo("Готово", f"✅ DataMatrix сохранён в {out_path} и отправлен на принтер.")
    except Exception as e:
        messagebox.showerror("Ошибка генерации", str(e))

# --- Интерфейс tkinter ---
root = tk.Tk()
root.title("DataMatrix → DataMatrix Generator")
root.geometry("600x500")

frame = tk.Frame(root)
frame.pack(pady=10)

btn_select = tk.Button(frame, text="📷 Считать DataMatrix", command=on_select_image, width=25)
btn_select.grid(row=0, column=0, padx=10)

btn_generate = tk.Button(frame, text="🧾 Сформировать итоговый DataMatrix", command=on_generate_dm, width=25)
btn_generate.grid(row=0, column=1, padx=10)

text_box = tk.Text(root, wrap=tk.WORD, height=25, width=70)
text_box.pack(pady=10)

root.mainloop()
