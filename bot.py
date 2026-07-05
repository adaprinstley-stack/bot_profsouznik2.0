from fastapi import FastAPI, Request
import requests

app = FastAPI()

# 🔐 токен MAX
TOKEN = "f9LHodD0cOIMUZmyfq_t-lNtX7DWfXMROP-dIxOkaWN7QjlOXx1NQ3EIW9JOt9wAS1bRLikxuEVswptZR1GU"
BASE_URL = "https://platform-api.max.ru"


# -------------------------
# 📊 логика теста
# -------------------------

QUESTIONS = [
    "Как часто вы чувствуете усталость на работе?",
    "Есть ли ощущение, что работа стала бессмысленной?",
    "Часто ли вы раздражаетесь на учеников?",
    "Есть ли проблемы со сном из-за работы?",
    "Чувствуете ли вы эмоциональное опустошение?"
]

answers = {
    "Никогда": 0,
    "Редко": 1,
    "Иногда": 2,
    "Часто": 3,
    "Постоянно": 4
}

# простое хранилище (в памяти)
user_state = {}


# -------------------------
# 📤 отправка сообщения
# -------------------------
def send_message(user_id: str, text: str, buttons=None):
    url = f"{BASE_URL}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "user_id": user_id,
        "text": text,
        "attachments": buttons or []
    }

    requests.post(url, json=payload, headers=headers)


# -------------------------
# 📊 результат теста
# -------------------------
def get_result(score):

    if score <= 12:
        return f"""🟢 Результат: {score}

Низкий риск выгорания.
Продолжайте балансировать работу и отдых."""

    elif score <= 25:
        return f"""🟡 Результат: {score}

Средний риск выгорания.
Рекомендуется снизить нагрузку и отдыхать."""

    else:
        return f"""🔴 Результат: {score}

Высокий риск выгорания.
Важно обратиться за поддержкой и снизить нагрузку."""


# -------------------------
# 📩 webhook MAX
# -------------------------
@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    if data.get("update_type") != "message_created":
        return {"ok": True}

    msg = data.get("message", {})
    user_id = msg.get("user_id")
    text = msg.get("text", "").strip()

    # -------------------------
    # 🟢 старт
    # -------------------------
    if text == "/start":

        user_state[user_id] = {
            "index": 0,
            "score": 0
        }

        send_message(
            user_id,
            "🤝 Бот 'Учитель в ресурсе'\n\nНажмите 'Начать тест' или напишите 1",
        )
        return {"ok": True}

    # -------------------------
    # 🟢 старт теста
    # -------------------------
    if text == "1":

        user_state[user_id] = {
            "index": 0,
            "score": 0
        }

        send_message(user_id, QUESTIONS[0])
        return {"ok": True}

    # -------------------------
    # 🟢 если пользователь проходит тест
    # -------------------------
    if user_id in user_state:

        state = user_state[user_id]

        if text in answers:

            state["score"] += answers[text]
            state["index"] += 1

            # если тест закончился
            if state["index"] >= len(QUESTIONS):

                result = get_result(state["score"])

                send_message(user_id, result)

                del user_state[user_id]
                return {"ok": True}

            # следующий вопрос
            send_message(user_id, QUESTIONS[state["index"]])
            return {"ok": True}

    # -------------------------
    # 🟢 помощь
    # -------------------------
    if text == "помощь":
        send_message(user_id, "Напишите /start чтобы начать тест")
        return {"ok": True}

    # -------------------------
    # 🟢 fallback
    # -------------------------
    send_message(user_id, "Напишите /start чтобы начать работу")
    return {"ok": True}
