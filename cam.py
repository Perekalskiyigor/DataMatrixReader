import gxipy as gx
import cv2
import os
from datetime import datetime

def capture_image(folder=".", prefix="snapshot"):
    """
    Захватывает один кадр с первой подключенной камеры и сохраняет его
    в папку с именем файла формата: YYYY-MM-DD_HH-MM-SS_номер.png
    
    :param folder: Папка для сохранения изображений
    :param prefix: Префикс имени файла
    :return: Полный путь к сохраненному изображению или None, если не удалось
    """
    # Создаём менеджер устройств
    system = gx.DeviceManager()

    # Обновляем список камер
    dev_num = system.update_device_list()
    if dev_num == 0:
        print("Камера не найдена!")
        return None

    # Открываем первую камеру
    cam = system.open_device_by_index(1)
    if cam is None:
        print("Не удалось открыть камеру")
        return None

    try:
        # Запускаем поток
        cam.stream_on()

        # Захватываем один кадр
        img = cam.data_stream[0].get_image()
        if img is None:
            print("Не удалось получить изображение")
            return None

        # Конвертируем в numpy
        img_array = img.get_numpy_array()

        # Формируем имя файла с датой, временем и порядковым номером
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        # Найдем следующий свободный номер
        n = 1
        while True:
            filename = f"{prefix}_{date_str}_{n}.png"
            filepath = os.path.join(folder, filename)
            if not os.path.exists(filepath):
                break
            n += 1

        # Сохраняем изображение
        cv2.imwrite(filepath, img_array)
        print(f"Изображение сохранено в {filepath}")

    finally:
        cam.stream_off()
        cam.close_device()

    return filepath
