import telebot
import schedule
import time
import os

# Указываем токен вашего бота
bot_token = '6654858930:AAFoLFagxCgVhfIlYSbGJjoynb1DTlqJvwE'

# Создаем экземпляр бота
bot = telebot.TeleBot(bot_token)

# Словарь для хранения папок и каналов
folders = {}

# Команды:

# Обрабатываем команду /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Привет! Я готов получать обновления от вас.")

@bot.message_handler(commands=['myfolders'])
def handle_myfolders(message):
    bot.reply_to(message, "Ищем папки....")
    bot.reply_to(f"Твои папки: {folders}")
#Обрабатываем команду для создания папки
@bot.message_handler(commands=['create_folder'])
def handle_create_folder(message):
    chat_id = message.chat.id
    bot.reply_to(message, "Введите название папки:")
    bot.register_next_step_handler(message, save_folder_name)

# Функция для сохранения названия папки
def save_folder_name(message):
    chat_id = message.chat.id
    folder_name = message.text
    folders[folder_name] = []
    bot.reply_to(message, f"Папка {folder_name} успешно создана.")

# Обрабатываем команду для добавления канала в папку
@bot.message_handler(commands=['add_channel'])
def handle_add_channel(message):
    chat_id = message.chat.id
    bot.reply_to(message, "Введите ссылку на канал, который вы хотите добавить:")
    bot.register_next_step_handler(message, save_channel_link)

# Функция для сохранения ссылки на канал
def save_channel_link(message):
    chat_id = message.chat.id
    channel_link = message.text
    bot.reply_to(message, "Введите название папки, в которую вы хотите добавить канал:")
    bot.register_next_step_handler(message, save_channel_to_folder, channel_link)

# Функция для сохранения канала в папку
def save_channel_to_folder(message, channel_link):
    chat_id = message.chat.id
    folder_name = message.text
    if folder_name not in folders:
        bot.reply_to(message, "Папка не найдена.")
        return
    folders[folder_name].append(channel_link)
    bot.reply_to(message, f"Канал {channel_link} успешно добавлен в папку {folder_name}.")

# Функция для проверки, является ли сообщение из канала в папке
def is_message_from_channel_in_folder(message, folder_name):
    chat_id = message.chat.id
    if folder_name not in folders:
        return False
    channel_links = folders[folder_name]
    return message.chat.username in channel_links

# Функция для отправки сообщения в личные сообщения пользователя
def send_message_to_private_chat(message):
    for folder_name, channel_links in folders.items():
        if message.chat.username in channel_links:
            bot.send_message(chat_id, message.text)

# Запускаем бота
bot.polling()

# Устанавливаем периодическую задачу для получения обновлений
def get_updates_job():
    updates = bot.get_updates()
    for update in updates:
        message = update.message
        for folder_name in folders.keys():
            if is_message_from_channel_in_folder(message, folder_name):
                send_message_to_private_chat(message)

# Запускаем периодическую задачу каждые 5 секунд
schedule.every(5).seconds.do(get_updates_job)

while True:
    schedule.run_pending()
    time.sleep(1)