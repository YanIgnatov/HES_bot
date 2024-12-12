import json
import os
import telebot
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaDocument

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Загрузка токена из файла
def load_token():
    with open('token.txt', 'r', encoding='utf-8') as file:
        return file.read().strip()


# Загрузка сообщения из JSON-файла
def load_message(file_name):
    with open(f'data/{file_name}', 'r', encoding='utf-8') as file:
        return json.load(file)


# Инициализация бота
bot = telebot.TeleBot(load_token(), parse_mode=None)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_message(message.chat.id, "welcome_message.json")


# Отправка сообщения с кнопками и вложениями
def send_message(chat_id, file_name):
    try:
        msg = load_message(file_name)
        text = msg["text"]
        attachments = [a for a in msg.get("attachments", []) if a]  # Убираем None из вложений
        buttons = [
            [InlineKeyboardButton(btn_text, callback_data=key)]
            for btn_text, key in msg["buttons"].items()
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        # Если нет вложений
        if not attachments:
            bot.send_message(chat_id, text, reply_markup=keyboard)

        # Если одно вложение (документ или изображение)
        elif len(attachments) == 1:
            attachment = attachments[0]
            if os.path.exists(f'data/{attachment}'):
                with open(f'data/{attachment}', 'rb') as file:
                    if attachment.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        # Отправка фото с текстом и кнопками
                        bot.send_photo(chat_id, file, caption=text, reply_markup=keyboard)
                    else:
                        # Отправка документа с текстом и кнопками
                        bot.send_document(chat_id, file, caption=text, reply_markup=keyboard)

        # Если несколько документов
        elif all(attachment.endswith(('.pdf', '.docx', '.txt')) for attachment in attachments):
            bot.send_message(chat_id, text)  # Отправка текста отдельно
            media_group = [InputMediaDocument(open(f'data/{attachment}', 'rb')) for attachment in attachments if os.path.exists(f'data/{attachment}')]
            bot.send_media_group(chat_id, media_group)
            # Отправка пустого сообщения с кнопками
            bot.send_message(chat_id, "ᅠ", reply_markup=keyboard)  # Спецсимвол используется для отправки пустого сообщения

        # Если несколько изображений
        elif all(attachment.endswith(('.jpg', '.jpeg', '.png', '.gif')) for attachment in attachments):
            bot.send_message(chat_id, text)  # Отправка текста отдельно
            media_group = [InputMediaPhoto(open(f'data/{attachment}', 'rb')) for attachment in attachments if os.path.exists(f'data/{attachment}')]
            bot.send_media_group(chat_id, media_group)
            # Отправка пустого сообщения с кнопками
            bot.send_message(chat_id, "ᅠ", reply_markup=keyboard)  # Спецсимвол используется для отправки пустого сообщения

        # Если вложения разнородные или больше одного изображения/документа
        else:
            bot.send_message(chat_id, text)  # Отправка текста отдельно
            media_group = []
            for attachment in attachments:
                if os.path.exists(f'data/{attachment}'):
                    if attachment.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        media_group.append(InputMediaPhoto(open(f'data/{attachment}', 'rb')))
                    else:
                        bot.send_document(chat_id, open(f'data/{attachment}', 'rb'))
            if media_group:
                bot.send_media_group(chat_id, media_group)
            # Отправка пустого сообщения с кнопками
            bot.send_message(chat_id, "ᅠ", reply_markup=keyboard)  # Спецсимвол используется для отправки пустого сообщения

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")


# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def process_callback(call):
    try:
        send_message(call.message.chat.id, call.data)
        bot.answer_callback_query(call.id)
    except Exception as e:
        logging.error(f"Произошла ошибка при обработке запроса: {e}")



# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=120, long_polling_timeout=5)