import telebot
import schedule
import time
import os
import sqlite3
import random
#база данных
def create(): # создание таблицы
    connect = sqlite3.connect('data.db')
    cursor = connect.cursor()
    zapros = f'''create table if not exists forges(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name Text,
        lincs TEXT
    );'''
    cursor.execute(zapros)
    connect.commit()
    cursor.close()
create()

def read_table(): #чтение всех записей
    connect = sqlite3.connect('data.db')
    cursor = connect.cursor()
    cursor.execute(f'select * FROM forges')
    table = cursor.fetchall()
    retrn = []
    for item in table:
        retrn.append(item)
    return retrn

def write_table(name): #создание папки (записи) name - имя папки,linc - адрес канала
    connect = sqlite3.connect('data.db')
    cursor = connect.cursor()
    cursor.execute("INSERT INTO forges (name) VALUES ('{name}')".format(name = name))
    cursor.close()
    connect.commit()

def add_linc(name,linc): # Добавление ссылки
    lincs = None
    for i in read_table():
        if i[1] == name:
            if i[2] == None:
                lincs = linc
                break
            tmp = i[2].split()
            print(tmp)

            lincs = " ".join(list(set(tmp)))
            break
    connect = sqlite3.connect('data.db')
    cursor = connect.cursor()
    cursor.execute(f"UPDATE forges SET lincs = '{lincs}' WHERE name = '{name}'")
    cursor.close()
    connect.commit()

def delete(id):
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM forges WHERE id = {id}")
    connection.commit()
    connection.close()
#_______________________________________________________________________________
#телеграмм-бот

# Указываем токен вашего бота
bot_token = '6654858930:AAFoLFagxCgVhfIlYSbGJjoynb1DTlqJvwE'
# Создаем экземпляр бота
bot = telebot.TeleBot(bot_token)

texts = ["https://t.me/physics_lib/10419",
         "https://t.me/stackoverflw/1797",
         "https://t.me/stackoverflw/1794",
         "https://t.me/+T1i5nO0m_h01ZDky",
         "https://t.me/physics_lib/10417",
         "https://t.me/c/1641577376/1969",
         "https://t.me/StarshipNewsLive/6957",
         "https://t.me/sandfacts/1441"
]
user_texts = {}

folders = []
# Список для хранения папок и каналов
for i in read_table():
    folders.append(i[1])

# Команды:

# Обрабатываем команду /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Привет! Я готов получать обновления от вас.")

@bot.message_handler(commands=["shownews"])
def shownews(message):
    # Выбираем случайный текст из списка
    text = random.choice(texts)
    user_texts[message.from_user.id] = text
    # Отправляем текст пользователю и просим его переписать его
    bot.reply_to(message, f":\n{text}")

@bot.message_handler(commands=['select_folder'])
def handle_myfolders(message):
    bot.reply_to(message, "Ищем папки....")
    text = ''
    if len(folders) > 0:
        for i in read_table():
            text = i[1] + '\n'
        bot.reply_to(message,f"Твои папки:\n{text}")
    else:
        bot.reply_to(message, "У вас нету папок :(")
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
    write_table(folder_name)
    folders.append(folder_name)
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
        bot.reply_to(message, "Папка не найдена :(")
        return
    add_linc(folder_name,channel_link)
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
        for folder_name in folders:
            if is_message_from_channel_in_folder(message, folder_name):
                send_message_to_private_chat(message)

# Запускаем периодическую задачу каждые 5 секунд
schedule.every(5).seconds.do(get_updates_job)

while True:
    schedule.run_pending()
    time.sleep(1)