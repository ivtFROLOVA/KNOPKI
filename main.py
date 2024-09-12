from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Токен бота
BOT_TOKEN = '6730354356:AAFDjPDiSwGRZ-eU8qGirwD7E5-cstby3uo'

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализируем билдер
kb_builder = ReplyKeyboardBuilder()

# Создаем кнопки
survey_btn = KeyboardButton(text='Участвовать в опросе')
quiz_btn = KeyboardButton(text='Участвовать в викторине')

# Добавляем кнопки в билдер
kb_builder.row(survey_btn, quiz_btn, width=2)

# Создаем объект клавиатуры
keyboard: ReplyKeyboardMarkup = kb_builder.as_markup(
    resize_keyboard=True,
    one_time_keyboard=True
)

survey_questions = [
    ("Вы спите?", ["да", "нет"]),
    ("Вы любите учиться?", ["да", "нет"]),
    ("Вы хотите домой?", ["да", "нет"]),
]

quiz_questions = [
    ("Какого цвета небо?", ["Синее", "Да", "Красное"], "Синее"),
    ("Апельсин - это фрукт или овощ?", ["Фрукт", "Ягода", "Я овощ"], "Фрукт"),
    ("Как списать на контрольной?", ["Выучить", "Никак", "Не придти"], "Никак"),
]

# Переменные для хранения состояния пользователя
user_data = {}


# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("ПОМОГИ МНЕ!!! (стать лучше)", reply_markup=keyboard)


# Обработчик кнопки "Пройти опрос"
@dp.message(lambda message: message.text == 'Участвовать в опросе')
async def start_survey(message: Message):
    user_data[message.from_user.id] = {"survey_step": 0, "survey_answers": []}
    await ask_survey_question(message)


async def ask_survey_question(message: Message):
    user_id = message.from_user.id
    step = user_data[user_id]["survey_step"]
    question, options = survey_questions[step]
    kb_builder = ReplyKeyboardBuilder()
    for option in options:
        kb_builder.button(text=option)
    keyboard = kb_builder.as_markup(resize_keyboard=True)
    await message.answer(question, reply_markup=keyboard)


@dp.message(lambda message: message.text in [option for q, o in survey_questions for option in o])
async def handle_survey_answer(message: Message):
    user_id = message.from_user.id
    step = user_data[user_id]["survey_step"]
    answer = message.text
    question = survey_questions[step][0]

    # Сохраняем ответ и вопрос
    user_data[user_id]["survey_answers"].append((question, answer))

    # Если есть еще вопросы
    if step + 1 < len(survey_questions):
        user_data[user_id]["survey_step"] += 1
        await ask_survey_question(message)
    else:
        # Выводим вопросы и ответы
        responses = "\n".join([f"{q}: {a}" for q, a in user_data[user_id]["survey_answers"]])
        await message.answer(f"Ваши ответы:\n{responses}", reply_markup=keyboard)


# Обработчик кнопки "Пройти викторину"
@dp.message(lambda message: message.text == 'Участвовать в викторине')
async def start_quiz(message: Message):
    user_data[message.from_user.id] = {"quiz_step": 0, "correct_answers": 0, "incorrect_answers": 0}
    await ask_quiz_question(message)


async def ask_quiz_question(message: Message):
    user_id = message.from_user.id
    step = user_data[user_id]["quiz_step"]
    question, options, _ = quiz_questions[step]
    kb_builder = ReplyKeyboardBuilder()
    for option in options:
        kb_builder.button(text=option)
    keyboard = kb_builder.as_markup(resize_keyboard=True)
    await message.answer(question, reply_markup=keyboard)


@dp.message(lambda message: message.text in [option for q, o, a in quiz_questions for option in o])
async def handle_quiz_answer(message: Message):
    user_id = message.from_user.id
    step = user_data[user_id]["quiz_step"]
    _, _, correct_answer = quiz_questions[step]

    if message.text == correct_answer:
        user_data[user_id]["correct_answers"] += 1
        await message.answer("Угадал :D")
    else:
        user_data[user_id]["incorrect_answers"] += 1
        await message.answer(f"Не угадал :(. Правильный ответ: {correct_answer}")

    # Если есть еще вопросы
    if step + 1 < len(quiz_questions):
        user_data[user_id]["quiz_step"] += 1
        await ask_quiz_question(message)
    else:
        correct = user_data[user_id]["correct_answers"]
        incorrect = user_data[user_id]["incorrect_answers"]
        await message.answer(f"КОНЕЕЕЕЦ! Верные ответы: {correct}, Неверные ответы: {incorrect}", reply_markup=keyboard)


# Запуск бота
if __name__ == '__main__':
    dp.run_polling(bot)
