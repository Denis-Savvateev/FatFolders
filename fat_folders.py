import logging
import logging.handlers
import os

from settings import (
    START_PATH,
    MIN_FOLDER_SIZE_GB,
    LOGFILE_PATH,
    LOG_MAX_SIZE
)

if not os.path.exists(LOGFILE_PATH):
    os.makedirs(os.path.dirname(LOGFILE_PATH), exist_ok=True)

logging.basicConfig(
    encoding='utf-8',
    format=(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ),
    level=logging.DEBUG,
    handlers=[
        logging.handlers.RotatingFileHandler(
            filename=LOGFILE_PATH,
            maxBytes=LOG_MAX_SIZE,
            backupCount=5,
            encoding='utf-8',
        )
    ],
)


def get_folder_size(folder):
    total_size = 0
    for path, dirs, files in os.walk(folder):
        for f in files:
            fp = os.path.join(path, f)
            # Добавляем размер файла к общему размеру папки
            try:
                total_size += os.path.getsize(fp)
            except Exception as e:
                logging.error(f'Ошибка доступа к файлу: {e}')
    return total_size


def find_large_folders(start_path, min_size_gb=10):
    min_size_bytes = min_size_gb * 1024**3  # Конвертируем Гб в байты
    large_folders = []
    
    for path, dirs, files in os.walk(start_path):
        folder_size = get_folder_size(path)
        if folder_size >= min_size_bytes:
            large_folders.append((path, folder_size))
    
    return large_folders

# Пример использования
large_folders = find_large_folders(START_PATH, MIN_FOLDER_SIZE_GB)

for folder, size in large_folders:
    print(f"Folder: {folder}, Size: {size / (1024**3):.2f} GB")
