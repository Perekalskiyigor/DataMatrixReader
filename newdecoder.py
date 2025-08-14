import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from pylibdmtx.pylibdmtx import decode
import qrcode
from PIL import Image, ImageTk

# Глобальное хранилище считанных данных
decoded_data = []

def read_datamatrix_whole_image(image_path):
    image = cv2.imread(image_path)
    decoded_objects = decode(image)

    if not decoded_objects:
        messagebox.showwarning("Внимание", "⚠️ DataMatrix-коды не найдены на изображении.")
        return []

    results = []
    for obj in decoded_objects:
        data = obj.data.decode('utf-8')
        results.append(data)

    return results

def generate_big_qr(data_list, output_path="big_qr.png"):
    combined_data = ",".join(data_list)
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4,
    )
    qr.add_data(combined_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    messagebox.showinfo("Готово", f"✅ QR-код сохранён в {output_path}")

def on_select_image():
    global decoded_data
    file_path = filedialog.askopenfilename(
        title="Выберите изображение",
        filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp")]
    )
    if not file_path:
        return

    decoded_data = read_datamatrix_whole_image(file_path)

    text_box.delete("1.0", tk.END)
    for i, item in enumerate(decoded_data, 1):
        text_box.insert(tk.END, f"{i:02d}: {item}\n")

def on_generate_qr():
    if not decoded_data:
        messagebox.showwarning("Ошибка", "Нет считанных данных для QR-кода.")
        return
    generate_big_qr(decoded_data)

# --- Интерфейс tkinter ---
root = tk.Tk()
root.title("DataMatrix -> QR Generator")
root.geometry("600x500")

frame = tk.Frame(root)
frame.pack(pady=10)

btn_select = tk.Button(frame, text="📷 Считать DataMatrix", command=on_select_image, width=25)
btn_select.grid(row=0, column=0, padx=10)

btn_generate = tk.Button(frame, text="🧾 Сформировать итоговый QR", command=on_generate_qr, width=25)
btn_generate.grid(row=0, column=1, padx=10)

text_box = tk.Text(root, wrap=tk.WORD, height=25, width=70)
text_box.pack(pady=10)

root.mainloop()
