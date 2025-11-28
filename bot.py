import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from config import TELEGRAM_TOKEN, CURRENCY_API_KEY

API_URL = "https://api.currencyapi.com/v3/latest"

AVAILABLE_CURRENCIES = [
    "USD", "EUR", "UAH", "GBP", "PLN", "CAD", "CHF", "JPY", "CNY",
    "AUD", "SEK", "NOK", "DKK", "CZK", "HUF", "RON", "BGN", "TRY",
    "ZAR", "MXN"
]


def get_all_rates(base="USD"):
    params = {"apikey": CURRENCY_API_KEY, "base_currency": base}
    response = requests.get(API_URL, params=params).json()
    return response.get("data", {})


def get_rate(base: str, target: str):
    data = get_all_rates(base)
    if target.upper() not in data:
        return None
    return data[target.upper()]["value"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Вітаю! Я бот-конвертер валют.\n"
        "Доступні команди:\n"
        "/rates – переглянути курси валют\n"
        "/currencies – доступні валютні коди\n"
        "/help – інструкція\n\n"
        "Щоб конвертувати:\n"
        "➡️ 100 USD EUR\n"
        "➡️ 250 EUR to USD\n"
    )
    await update.message.reply_text(text)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📘 Приклади використання:\n"
        "- 50 USD EUR\n"
        "- 100 EUR to USD\n"
        "- 100 uah usd\n\n"
        "Команди:\n"
        "/rates – курси валют\n"
        "/currencies – які валюти доступні"
    )
    await update.message.reply_text(text)


async def currencies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    curr_list = ", ".join(AVAILABLE_CURRENCIES)
    await update.message.reply_text(f"🌍 Доступні валюти:\n{curr_list}")


async def rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    base = "USD"  # базова валюта
    data = get_all_rates(base)

    message = f"💱 Курси валют (база: {base}):\n\n"
    for code in AVAILABLE_CURRENCIES:
        if code == base:
            continue
        if code in data:
            rate = data[code]["value"]
            message += f"• {code}: {rate:.3f}\n"

    await update.message.reply_text(message)


async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("to", "").replace("TO", "")
    parts = text.split()

    if len(parts) != 3:
        await update.message.reply_text("❗ Формат має бути: 100 USD EUR")
        return

    amount, base, target = parts

    try:
        amount = float(amount)
    except ValueError:
        await update.message.reply_text("❗ Перша частина має бути числом.")
        return

    rate = get_rate(base, target)
    if rate is None:
        await update.message.reply_text("❗ Валюта не знайдена.")
        return

    result = amount * rate

    await update.message.reply_text(
        f"💱 Конвертація:\n"
        f"{amount} {base.upper()} → {target.upper()}\n\n"
        f"📌 Результат: {result:.2f} {target.upper()}"
    )


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Команди
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("rates", rates))
    app.add_handler(CommandHandler("currencies", currencies))

    # Всі повідомлення — конвертація
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert))

    app.run_polling()


if __name__ == "__main__":
    main()
