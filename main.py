from aiogram import Dispatcher, Bot, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

TOKEN_API = '6777356577:AAElutRBtfqcLAQsEw2ZfOglL3EirqFxOu8'
bot = Bot(token=TOKEN_API)
dp = Dispatcher(bot)

questions = [
    {"id": 1, "question": "Что такое Крым с географической точки зрения?", "options": ["Полуостров", "Материк", "Остров"], "answer": "0", "image": "https://krymoteka.ru/files/img/luchshie-plyazhi-kryma-dlya-otdyha-na-more12.jpg"},
    {"id": 2, "question": "Какой город является столицей Республики Крым?", "options": ["Севастополь", "Симферополь", "Ялта"], "answer": "1", "image": "https://avatars.dzeninfra.ru/get-zen_doc/3472554/pub_606321ef3ebe7f2d78ecaf87_6065a0507494b532e4e6a240/scale_1200"},
    {"id": 3, "question": "Какой памятник архитектуры и истории расположен на отвесной скале на южном берегу Крыма?", "options": ["Воронцовский дворец", "Большой каньон", "Ласточкино гнездо"], "answer": "2", "image": "https://s00.yaplakal.com/pics/pics_original/0/6/8/4122860.jpg"},
    {"id": 4, "question": "Какие крымские города носят звание «Город-герой»?", "options": ["Севастополь и Симферополь", "Керчь и Феодосия", "Керчь и Севастополь"], "answer": "2", "image": "https://avatars.mds.yandex.net/i?id=470d964c724b3f77cda20a504bd4fb1dae10ce33-12571073-images-thumbs&n=13"},
    {"id": 5, "question": "Когда Республика Крым была включена в состав Российской Федерации?", "options": ["18 марта 2014", "18 марта 2016", "18 марта 2020"], "answer": "0", "image": "https://ic.pics.livejournal.com/channel_sk1n/74795194/313105/313105_original.jpg"},
    {"id": 6, "question": "Что из перечисленного является символом воссоединения России и Крыма?", "options": ["Новый терминал аэропорта в Симферополе", "Крымский мост", "Трасса 'Таврида'"], "answer": "1", "image": "https://top-fon.com/uploads/posts/2023-01/1674619559_top-fon-com-p-fon-dlya-prezentatsii-yedinaya-rossiya-174.jpg"},
    {"id": 7, "question": "Что в переводе с Крымско-Татарского означает слово Крым?", "options": ["Крепость", "Берег", "Ров"], "answer": "0", "image": "https://avatars.mds.yandex.net/i?id=891319f6cdd7f280738ee9bcbf862cad88b50305-12149948-images-thumbs&n=13"},
    {"id": 8, "question": "Как называется этот памятник, установленный в Симферополе?", "options": ["Памятник добрым людям", "Памятник вежливым людям", "Памятник воспитанным людям"], "answer": "1", "image": "https://antimaidan.ru/sites/default/files/styles/large/public/news/21743854_2046067432085525_5176785461646635980_o.jpg?itok=4yHVv-Qh"},
    {"id": 9, "question": "Какова протяженность Крымского моста?", "options": ["Около 26 км", "Около 7 км", "Около 19 км"], "answer": "2", "image": "https://mykaleidoscope.ru/x/uploads/posts/2022-09/1663087166_6-mykaleidoscope-ru-p-krimskii-most-oboi-6.jpg"}
]

user_states = {}

async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="Перезапустить бота"),
        types.BotCommand(command="/quiz", description="Начать викторину")
    ]
    await bot.set_my_commands(commands)

def generate_markup(question):
    markup = InlineKeyboardMarkup()
    for idx, option in enumerate(question["options"]):
        button = InlineKeyboardButton(option, callback_data=str(idx))
        markup.add(button)
    return markup

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.answer('Привет, чтобы пройти викторину напиши /quiz')

@dp.message_handler(commands=["quiz"])
async def start_quiz(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = {"questions": random.sample(questions, len(questions)), "correct_answers": 0}
    await send_question(message)

async def send_question(message: types.Message):
    user_id = message.from_user.id
    state = user_states[user_id]

    if state["questions"]:
        question = state["questions"].pop(0)
        state["last_question"] = question

        markup = generate_markup(question)

        if "image" in question:
            sent_message = await bot.send_photo(chat_id=user_id, photo=question["image"], caption=question['question'], reply_markup=markup)
        else:
            sent_message = await bot.send_message(chat_id=user_id, text=question['question'], reply_markup=markup)

        state["message_id"] = sent_message.message_id
    else:
        if "message_id" in state:
            await bot.delete_message(chat_id=user_id, message_id=state["message_id"])
        await bot.send_message(chat_id=user_id, text=f"Викторина окончена! Вы правильно ответили на {state['correct_answers']} из {len(questions)} вопросов.")
        del user_states[user_id]

@dp.callback_query_handler(lambda c: True)
async def process_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    state = user_states.get(user_id, {})

    if "last_question" not in state:
        await callback_query.answer("Произошла ошибка, попробуйте начать викторину заново с помощью команды /start.", show_alert=True)
        return

    question = state["last_question"]
    correct_answer_index = int(question["answer"])
    selected_option_index = int(callback_query.data)

    if "message_id" in state:
        try:
            await bot.delete_message(chat_id=user_id, message_id=state["message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    if selected_option_index == correct_answer_index:
        state["correct_answers"] += 1
        await callback_query.answer("Верно!", show_alert=True)
    else:
        await callback_query.answer("Неправильно.", show_alert=True)

    if state["questions"]:
        await send_question_from_callback(user_id)
    else:
        final_text = f"Викторина окончена! Вы правильно ответили на {state['correct_answers']} из {len(questions)} вопросов."
        await bot.send_message(chat_id=user_id, text=final_text)
        del user_states[user_id]

async def send_question_from_callback(user_id):
    state = user_states.get(user_id)
    if not state or not state["questions"]:
        return

    question = state["questions"].pop(0)
    state["last_question"] = question

    markup = generate_markup(question)

    if "image" in question:
        sent_message = await bot.send_photo(chat_id=user_id, photo=question["image"], caption=question['question'], reply_markup=markup)
    else:
        sent_message = await bot.send_message(chat_id=user_id, text=question['question'], reply_markup=markup)

    state["message_id"] = sent_message.message_id

async def on_startup(dispatcher):
    await set_commands(dispatcher.bot)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)