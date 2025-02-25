import asyncio
import logging
import logging.handlers
import os

import telegram

from settings import (
    START_PATH,
    MIN_FOLDER_SIZE_GB,
    LOGFILE_PATH,
    LOG_MAX_SIZE,
    NUMBER_OF_LOG_FILES,
    TOKEN,
    MY_CHAT_ID,
)

if not os.path.exists(LOGFILE_PATH):
    os.makedirs(os.path.dirname(LOGFILE_PATH), exist_ok=True)

logging.basicConfig(
    encoding='utf-8',
    format=(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ),
    level=logging.INFO,
    handlers=[
        logging.handlers.RotatingFileHandler(
            filename=LOGFILE_PATH,
            maxBytes=LOG_MAX_SIZE,
            backupCount=NUMBER_OF_LOG_FILES,
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
        if path == start_path:
            continue
        folder_size = get_folder_size(path)
        if folder_size >= min_size_bytes:
            large_folders.append((path, folder_size))
    return large_folders


async def send_telegram(text: str):
    bot: telegram.Bot = telegram.Bot(token=TOKEN)
    try:
        await bot.send_message(MY_CHAT_ID, text)
        logging.debug(f'Отправлено сообщение "{text}"')
    except telegram.TelegramError as error:
        logging.error(f'Ошибка при отправке сообщения "{text}" '
                      f'в Telegram: {error}')


def make_text(large_folders: list):
    if len(large_folders) == 1:
        finded: str = (
            f'Обнаружен каталог размером больше {MIN_FOLDER_SIZE_GB} Гб:'
        )
    elif len(large_folders) > 1:
        finded: str = (
            f'Обнаружены каталоги размером больше {MIN_FOLDER_SIZE_GB} Гб:'
        )
    message_text: str = f'{finded}\n'
    for folder, size in large_folders:
        message_text += f'{folder}; Размер: {size / (1024**3):.2f} GB\n'
    return message_text


def main():
    large_folders = find_large_folders(START_PATH, MIN_FOLDER_SIZE_GB)
    if large_folders:
        text = make_text(large_folders)
        logging.info(text)
        asyncio.run(send_telegram(text))
    else:
        logging.info(
            f'Каталогов размером больше {MIN_FOLDER_SIZE_GB} Гб не обнаружено'
        )


if __name__ == '__main__':
    main()
