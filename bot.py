import os
import asyncio
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
import openai

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Tokens
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize bot
bot = Bot(token=TELEGRAM_TOKEN)

# Initialize dispatcher
dp = Dispatcher()

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Prompt
LEGAL_PROMPT = """
Siz tajribali va professional huquqshunos yurist assistentsiz. Faqat O‘zbekiston Respublikasi qonunchiligi asosida javob bering. 
Javobingiz rasmiy, tushunarli, grammatik jihatdan to‘g‘ri va adabiy o‘zbek tilida bo‘lishi kerak. 
Jinoyat kodeksi, Fuqarolik kodeksi, Ma’muriy javobgarlik to‘g‘risidagi kodeks va boshqa qonun hujjatlaridan foydalaning. 
Moddalarni aniq raqamlar bilan ko‘rsating. 
Agar savol noaniq bo‘lsa yoki huquqiy masalaga taalluqli bo‘lmasa, foydalanuvchini advokatga murojaat qilishga undang.
"""

# Huquqiy savolni aniqlovchi funksiya
async def is_legal_question(question: str) -> bool:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Foydalanuvchi savoli huquqiy mavzuda bo‘lsa 'ha', bo‘lmasa 'yo‘q' deb javob qaytaring."},
            {"role": "user", "content": question},
        ],
        max_tokens=3,
        temperature=0.0,
    )
    answer = response['choices'][0]['message']['content'].strip().lower()
    return answer == "ha"

# Xabarlar uchun handler
@dp.message(F.text)
async def handle_message(message: Message):
    question = message.text
    if await is_legal_question(question):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": LEGAL_PROMPT},
                {"role": "user", "content": question},
            ],
            max_tokens=1000,
            temperature=0.1,
        )
        await message.answer(response['choices'][0]['message']['content'])
    else:
        await message.answer("Ushbu savol huquqiy masalaga tegishli emas. Iltimos, aniqroq va huquqiy savol yuboring.")

# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
