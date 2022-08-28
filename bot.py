import telebot
from telebot import types
import db_func
import pandas as pd
from functools import wraps

token = 'ваш токен'
bot = telebot.TeleBot(token)
db_func.create_tables()

state = {
    'REGISTERED',
    'AUTHENTICATED',
}

roles = [
    'Аналитик',
    'Продакт менеджер'
]

role_group = {
    'analyst': 'Аналитик',
    'product': 'Продакт менеджер',
}

role_commands = {
    'product': ['command1'],
    'analyst': ['command1', 'command2']
}
available_commands = [*list(role_group.values()), *['command1', 'command2']]


def check_user_role(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_role = None
        try:
            print(str(args[0].chat.id))
            user_role = db_func.check_role(str(args[0].chat.id))
            print(user_role)
            if not user_role:
                raise Exception(f'{id} не зарегистрирован')
        except Exception as e:
            print(e)
            bot.send_message(args[0].chat.id, 'Вы не зарегистрированы')

        return f(user_role, *args, **kwargs)

    return decorated


@bot.message_handler(commands=['start'])
@check_user_role
def start(user_role, message):
    if not user_role:
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        item1 = types.KeyboardButton('Регистрация')
        markup.add(item1)
        bot.send_message(
            message.chat.id, 'Нажми: \nРегистрация, что бы продолжить ', reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(
            message.chat.id, first_step_process)
    else:
        bot.send_message(message.chat.id, db_func.already_registered_text)
        redirect_by_user_role(message)


def first_step_process(message):
    if not (message.text in available_commands):
        pass

    if message.text == 'Регистрация':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(role_group['analyst'])
        item2 = types.KeyboardButton(role_group['product'])
        markup.add(item1, item2)

        bot.send_message(
            message.chat.id, text="Выбери, в какую группу тебя зарегистрировать", reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(
            message.chat.id, registration)


def registration(message):
    user = {
        'user_id': message.from_user.id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
        'job_group': message.text,
    }
    registrationMessage = db_func.register_user(
        user, message.chat.id, callback=bot.send_message)

    if db_func.success_text in registrationMessage or db_func.already_registered_text in registrationMessage:
        redirect_by_user_role(message)


@check_user_role
def redirect_by_user_role(user_role, message):
    if user_role == roles[0]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(role_commands['analyst'][0])
        item2 = types.KeyboardButton(role_commands['analyst'][1])
        markup.add(item1, item2)
        bot.send_message(message.chat.id,
                         text="Выбери команду:\ncommand1-сравнение значений со средними\ncommand2-проверка актуальности данных в файле",
                         reply_markup=markup)

    if user_role == roles[1]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(role_commands['product'][0])
        markup.add(item1)
        bot.send_message(message.chat.id,
                         text="Выбери команду:\ncommand1-сравнение значений со средними",
                         reply_markup=markup)


@bot.message_handler(regexp='command1')
@check_user_role
def command_1(user_role, message):
    if user_role:
        data = pd.read_excel('TG_BOT_DATA-3.xlsx')
        last_day = data.iloc[-1]['metrick1']
        last_30_value = data.iloc[-30:]['metrick1']
        avg = last_30_value.mean()
        median = last_30_value.median()
        return bot.send_message(message.chat.id, f'Для столбца metrick1:\nЗначение в последний день - {last_day}'
                                                 f'\nСреднее значение за последние 30 дней - {avg}'
                                                 f'\nМедианное значение за последние 30 дней - {median}')


@bot.message_handler(regexp='command2')
@check_user_role
def command_2(user_role, message):
    if user_role == roles[0]:
        data = pd.read_excel('TG_BOT_DATA-3.xlsx')
        actual_date = data.iloc[-1]['Date']
        return bot.send_message(message.chat.id, f'Данные актуальны на {actual_date}')


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.infinity_polling()
