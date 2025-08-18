import cv2
from pyzbar.pyzbar import decode
import qrcode


def read_barcodes(image_path):
    """
    Считывает все коды с изображения и возвращает список данных.
    """
    image = cv2.imread(image_path)
    barcodes = decode(image)

    data_list = []
    for barcode in barcodes:
        try:
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            print(f"Тип: {barcode_type}, Данные: {barcode_data}")
            data_list.append(barcode_data)
        except Exception as e:
            print(f"Ошибка при декодировании: {e}")
    
    return data_list


def generate_combined_qr(data_list, output_path='combined_qr.png'):
    """
    Формирует один QR-код из списка данных и сохраняет его как изображение.
    """
    if not data_list:
        print("Нет данных для генерации QR-кода.")
        return

    # Объединяем данные (можно через \n, или любой другой разделитель)
    combined_data = '\n'.join(data_list)

    # Генерируем QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(combined_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    print(f"Сохранён объединённый QR-код: {output_path}")


# Пример использования
if __name__ == "__main__":
    barcodes_data = read_barcodes("2025-08-14_11-52-46.png")
    generate_combined_qr(barcodes_data)
