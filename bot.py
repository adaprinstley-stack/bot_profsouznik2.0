from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


from questions import QUESTIONS

bot = Bot("f9LHodD0cOIMUZmyfq_t-lNtX7DWfXMROP-dIxOkaWN7QjlOXx1NQ3EIW9JOt9wAS1bRLikxuEVswptZR1GU")
dp = Dispatcher(storage=MemoryStorage())


class TestState(StatesGroup):
    answering = State()


answers = {
    "Никогда": 0,
    "Редко": 1,
    "Иногда": 2,
    "Часто": 3,
    "Постоянно": 4
}


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Пройти тест")],
        [KeyboardButton(text="🧘 Практики самопомощи")],
        [KeyboardButton(text="❤️ Чек-ин настроения")]
    ],
    resize_keyboard=True
)


test_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Никогда")],
        [KeyboardButton(text="Редко")],
        [KeyboardButton(text="Иногда")],
        [KeyboardButton(text="Часто")],
        [KeyboardButton(text="Постоянно")]
    ],
    resize_keyboard=True
)


@dp.message(CommandStart())
async def start(message: Message):

    text = """
🤝 Добро пожаловать в бот "Учитель в ресурсе"!

Этот бот поможет оценить риск эмоционального выгорания и получить рекомендации по самопомощи.

⚠️ Тест не является медицинской диагностикой.
"""

    await message.answer(text, reply_markup=main_menu)


@dp.message(F.text == "📝 Пройти тест")
async def start_test(message: Message, state: FSMContext):

    await state.set_state(TestState.answering)

    await state.update_data(index=0, score=0)

    await message.answer(
        QUESTIONS[0],
        reply_markup=test_keyboard
    )


@dp.message(TestState.answering)
async def process_answer(message: Message, state: FSMContext):

    if message.text not in answers:
        return

    data = await state.get_data()

    score = data["score"] + answers[message.text]
    index = data["index"] + 1

    if index == len(QUESTIONS):

        await state.clear()

        result = get_result(score)

        await message.answer(
            result,
            reply_markup=main_menu
        )

        return

    await state.update_data(
        index=index,
        score=score
    )

    await message.answer(
        QUESTIONS[index]
    )


def get_result(score):

    if score <= 12:

        return f"""
🟢 Ваш результат: {score} баллов

Низкий риск выгорания.

Продолжайте соблюдать баланс между работой и отдыхом.

✅ полноценный сон
✅ физическая активность
✅ хобби
✅ поддержка коллег

Профилактика всегда лучше восстановления.
"""

    elif score <= 25:

        return f"""
🟡 Ваш результат: {score} баллов

Средний риск выгорания.

Рекомендуется:

✅ сократить дополнительную нагрузку
✅ выделять время без работы
✅ использовать техники расслабления
✅ обсуждать сложности с коллегами

Если состояние сохраняется долго, обратитесь к специалисту.
"""

    else:

        return f"""
🔴 Ваш результат: {score} баллов

Высокий риск эмоционального выгорания.

Помните: это не слабость, а реакция организма на перегрузку.

Рекомендуется:

✅ обратиться за поддержкой
✅ обсудить снижение нагрузки
✅ наладить режим сна
✅ проконсультироваться с психологом

Берегите себя ❤️
"""


@dp.message(F.text == "🧘 Практики самопомощи")
async def self_help(message: Message):

    text = """
🧘 Практики самопомощи

🌬 Дыхание 4-4-6
Вдох 4 секунды
Задержка 4 секунды
Выдох 6 секунд

☕ После уроков:
✅ выпить воды
✅ пройтись 10 минут
✅ не открывать рабочий чат хотя бы час

💤 Сон:
✅ без телефона за час до сна
✅ проветривать комнату
✅ ложиться в одно время
"""

    await message.answer(text)


@dp.message(F.text == "❤️ Чек-ин настроения")
async def mood(message: Message):

    await message.answer("""
Как вы себя чувствуете сегодня?

😊 В ресурсе
😐 Устал(а)
😔 На пределе
""")


@dp.message(F.text == "😊 В ресурсе")
async def mood_good(message: Message):

    await message.answer(
        "Отлично! Продолжайте заботиться о себе ❤️"
    )


@dp.message(F.text == "😐 Устал(а)")
async def mood_mid(message: Message):

    await message.answer(
        "Попробуйте сегодня выделить хотя бы 30 минут только для себя."
    )


@dp.message(F.text == "😔 На пределе")
async def mood_bad(message: Message):

    await message.answer(
        "Вы не обязаны справляться в одиночку. Обратитесь за поддержкой к коллегам, близким или специалистам ❤️"
    )


if __name__ == "__main__":
    dp.run_polling(bot)