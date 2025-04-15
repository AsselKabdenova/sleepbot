import telebot
from telebot import types
import datetime

API_TOKEN = '7597043260:AAFK_OFEDx9er0YOYKVGmI9-nF7n_R3GTPk'
bot = telebot.TeleBot(API_TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "Привет! Я помогу тебе составить персональный план дня 🧠")
    bot.send_message(message.chat.id, "Со скольки до скольки у тебя пары? (например: 9:00-13:00) 🎓")
    bot.register_next_step_handler(message, ask_sleep_time)

def ask_sleep_time(message):
    user_data[message.chat.id]['classes'] = message.text
    bot.send_message(message.chat.id, "Во сколько ты планируешь лечь спать? (например: 23:30) 😴")
    bot.register_next_step_handler(message, ask_wakeup_time)

def ask_wakeup_time(message):
    user_data[message.chat.id]['sleep'] = message.text
    bot.send_message(message.chat.id, "Во сколько ты хочешь проснуться? (например: 07:00) ⏰")
    bot.register_next_step_handler(message, ask_rest_time)

def ask_rest_time(message):
    user_data[message.chat.id]['wake'] = message.text
    bot.send_message(message.chat.id, "Сколько часов ты хочешь отдохнуть завтра (кроме сна)? 🧘‍♂️")
    bot.register_next_step_handler(message, ask_fatigue)

def ask_fatigue(message):
    user_data[message.chat.id]['rest'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Да', 'Нет')
    bot.send_message(message.chat.id, "Ты чувствуешь усталость или сонливость днём? 😴", reply_markup=markup)
    bot.register_next_step_handler(message, ask_chrono)

def ask_chrono(message):
    user_data[message.chat.id]['fatigue'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Утром', 'Вечером')
    bot.send_message(message.chat.id, "Ты больше активен утром или вечером? 🐓🌙", reply_markup=markup)
    bot.register_next_step_handler(message, ask_schedule)

def ask_schedule(message):
    user_data[message.chat.id]['chronotype'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Строгое', 'Гибкое')
    bot.send_message(message.chat.id, "Ты предпочитаешь строгое расписание или гибкое? 📅", reply_markup=markup)
    bot.register_next_step_handler(message, ask_timezone)

def ask_timezone(message):
    user_data[message.chat.id]['schedule'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Да', 'Нет')
    bot.send_message(message.chat.id, "Раньше ты жил в регионе с другим временем? (например, Алматы)? 🌍", reply_markup=markup)
    bot.register_next_step_handler(message, ask_tasks)

def ask_tasks(message):
    user_data[message.chat.id]['timezone_shift'] = message.text == 'Да'
    bot.send_message(message.chat.id, "Какие задачи помимо уроков у тебя есть? Вводи по одной задаче, после каждой нажимай Enter. Когда закончишь — напиши 'Готово'. ✏️")
    user_data[message.chat.id]['tasks'] = []
    bot.register_next_step_handler(message, collect_tasks)

def collect_tasks(message):
    if message.text.lower() == 'готово':
        user_data[message.chat.id]['task_scores'] = []
        ask_task_rating(message, 0)
    else:
        user_data[message.chat.id]['tasks'].append(message.text)
        bot.register_next_step_handler(message, collect_tasks)

def ask_task_rating(message, idx):
    tasks = user_data[message.chat.id]['tasks']
    if idx >= len(tasks):
        generate_schedule(message)
        return
    bot.send_message(message.chat.id, f"На сколько баллов ты оценишь важность задачи: '{tasks[idx]}'? (от 1 до 5) 📝")
    bot.register_next_step_handler(message, lambda msg: save_rating(msg, idx))

def save_rating(message, idx):
    try:
        score = int(message.text)
    except ValueError:
        score = 3
    user_data[message.chat.id]['task_scores'].append((user_data[message.chat.id]['tasks'][idx], score))
    ask_task_rating(message, idx + 1)


def generate_schedule(message):
    data = user_data[message.chat.id]
    plan = "\n\U0001F4C5 Твой план на завтра:\n"
    plan += f"\u23F0 Подъем: {data['wake']}\n"
    plan += f"\U0001F4DA Пары: {data['classes']}\n"
    plan += f"\U0001F3E1 Отдых: {data['rest']} ч\n"
    for task, score in sorted(data['task_scores'], key=lambda x: -x[1]):
        plan += f"\u270D\ufe0f {task} (важность: {score})\n"
    plan += f"\U0001F634 Сон: {data['sleep']}\n"
    bot.send_message(message.chat.id, plan)

bot.infinity_polling()

