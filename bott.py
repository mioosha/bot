import telebot
import sqlite3
from telebot import types

TOKEN = "8289164985:AAFqMwLDpSnNBfEg_hUKO0wlxFTbB_mTWf8"
bot = telebot.TeleBot(TOKEN)

# --- База данных ---
conn = sqlite3.connect('requests.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    customer_info TEXT,
    wishes TEXT,
    date_start TEXT,
    date_end TEXT,
    item_count TEXT,
    work_clean TEXT,
    work_grind TEXT,
    work_primer TEXT,
    work_putty TEXT,
    work_ready_paint TEXT,
    work_painted TEXT,
    work_deglazed TEXT,
    work_boxes TEXT,
    work_sills TEXT,
    work_between_windows TEXT,
    extra_works TEXT
)
''')
conn.commit()

# --- Главное меню ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Старт")
    btn2 = types.KeyboardButton("Создать заявку")
    btn3 = types.KeyboardButton("Посмотреть все заявки")
    markup.row(btn1)
    markup.row(btn2, btn3)
    return markup

@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id,
                     "Добро пожаловать! Выберите действие:",
                     reply_markup=main_menu())

# --- Обработка выбора из главного меню ---
@bot.message_handler(func=lambda m: m.text == "Старт")
def handle_menu_start(message):
    bot.send_message(message.chat.id, "Используйте кнопки ниже для работы с ботом.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "Создать заявку")
def handle_menu_create(message):
    user_id = message.from_user.id
    user_states[user_id] = {"step": 0, "data": {}}
    bot.send_message(message.chat.id, "Введите ФИО и адрес заказчика:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: m.text == "Посмотреть все заявки")
def handle_menu_view(message):
    cursor.execute("SELECT id, customer_info, wishes, date_start, date_end, item_count, work_clean, work_grind, work_primer, work_putty, work_ready_paint, work_painted, work_deglazed, work_boxes, work_sills, work_between_windows, extra_works FROM requests")
    rows = cursor.fetchall()
    if not rows:
        bot.send_message(message.chat.id, "Список заявок пуст.", reply_markup=main_menu())
        return
    for r in rows:
        text = (
            f"№ {r[0]}\n"
            f"Заказчик: {r[1]}\n"
            f"Пожелания: {r[2]}\n"
            f"Сроки: {r[3]} — {r[4]}\n"
            f"Кол-во изделий: {r[5]}\n"
            f"Виды работ:\n"
            f"  - Зачистка краски: {r[6]}\n"
            f"  - Первичная шлифовка: {r[7]}\n"
            f"  - Грунт: {r[8]}\n"
            f"  - Шпатлевание: {r[9]}\n"
            f"  - Готово к окрашиванию: {r[10]}\n"
            f"  - Окрашено: {r[11]}\n"
            f"  - Расстекловка: {r[12]}\n"
            f"  - Коробки: {r[13]}\n"
            f"  - Подоконники: {r[14]}\n"
            f"  - Межоконное пространство: {r[15]}\n"
            f"Дополнительно: {r[16]}"
        )
        bot.send_message(message.chat.id, text, reply_markup=main_menu())

# --- Опрос по заявке с кнопками для yes/no ---
user_states = {}
fields = [
    ('customer_info', "Введите ФИО и адрес заказчика:"),
    ('wishes', "Опишите пожелания клиента:"),
    ('date_start', "Дата начала работ:"),
    ('date_end', "Дата окончания работ:"),
    ('item_count', "Общее количество изделий:"),
    ('work_clean', "Зачистка краски:", ["Да", "Нет"]),
    ('work_grind', "Первичная шлифовка:", ["Да", "Нет"]),
    ('work_primer', "Грунт:", ["Да", "Нет"]),
    ('work_putty', "Шпатлевание:", ["Да", "Нет"]),
    ('work_ready_paint', "Готово к окрашиванию:", ["Да", "Нет"]),
    ('work_painted', "Окрашено:", ["Да", "Нет"]),
    ('work_deglazed', "Расстекловка:", ["Да", "Нет"]),
    ('work_boxes', "Коробки:", ["Да", "Нет"]),
    ('work_sills', "Подоконники:", ["Да", "Нет"]),
    ('work_between_windows', "Межоконное пространство:", ["Да", "Нет"]),
    ('extra_works', "Опишите дополнительные работы (если есть):"),
]

@bot.message_handler(func=lambda m: m.from_user.id in user_states)
def handle_input(message):
    user_id = message.from_user.id
    state = user_states[user_id]
    step = state["step"]
    field = fields[step]
    key = field[0]
    state["data"][key] = message.text
    step += 1
    if step < len(fields):
        state["step"] = step
        next_field = fields[step]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if len(next_field) == 3:  # если есть варианты выбора
            for opt in next_field[2]:
                markup.add(types.KeyboardButton(opt))
            bot.send_message(message.chat.id, next_field[1], reply_markup=markup)
        else:
            bot.send_message(message.chat.id, next_field[1], reply_markup=types.ReplyKeyboardRemove())
    else:
        data = state["data"]
        cursor.execute('''
            INSERT INTO requests (
                user_id, customer_info, wishes, date_start, date_end, item_count,
                work_clean, work_grind, work_primer, work_putty, work_ready_paint,
                work_painted, work_deglazed, work_boxes, work_sills, work_between_windows, extra_works)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data['customer_info'], data['wishes'], data['date_start'], data['date_end'], data['item_count'],
            data['work_clean'], data['work_grind'], data['work_primer'], data['work_putty'],
            data['work_ready_paint'], data['work_painted'], data['work_deglazed'],
            data['work_boxes'], data['work_sills'], data['work_between_windows'], data['extra_works']
        ))
        conn.commit()
        bot.send_message(message.chat.id, "Заявка успешно сохранена!", reply_markup=main_menu())
        user_states.pop(user_id, None)

bot.polling(none_stop=True)
