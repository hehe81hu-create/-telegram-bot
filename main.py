import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8989872372:AAFpV6Y03zTu264m3tmO86PoyPHD1phl8js"
REPLICATE_API_TOKEN = "r8_Rw1gc4lORlJd5cKP4KbaysdUlMLUQxE0Vrv7g"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎬 Video Yaratish")],
        [KeyboardButton(text="ℹ️ Yordam")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "Seedance 2.0 orqali video yaratuvchi bot ishga tushdi.\n"
        "Boshlash uchun pastdagi tugmani bosing:",
        reply_markup=main_menu
    )

@dp.message(F.text == "🎬 Video Yaratish")
async def ask_prompt(message: types.Message):
    await message.answer("📝 Qanday video yaratmoqchisiz? Ingliz tilida batafsil yozib yuboring:")

@dp.message(F.text == "ℹ️ Yordam")
async def about_handler(message: types.Message):
    await message.answer("🤖 Bot matnli so'rovlar asosida 720p HD formatda video yaratib beradi.")

@dp.message(F.text & ~F.text.startswith("/"))
async def generate_video(message: types.Message):
    if message.text in ["🎬 Video Yaratish", "ℹ️ Yordam"]:
        return

    prompt = message.text
    status_msg = await message.answer("⏳ Video generatsiya qilinmoqda, iltimos kuting (1-2 daqiqa)...")

    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "bytedance/seedance-2.0",
        "input": {
            "prompt": prompt,
            "duration": 5,
            "resolution": "720p",
            "aspect_ratio": "16:9",
            "generate_audio": True
        }
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("https://api.replicate.com/v1/predictions", json=payload, headers=headers) as resp:
                if resp.status != 201:
                    err_text = await resp.text()
                    await status_msg.edit_text(f"❌ Xatolik yuz berdi: {err_text}")
                    return
                data = await resp.json()
                get_url = data.get("urls", {}).get("get")
                
            while True:
                await asyncio.sleep(4)
                async with session.get(get_url, headers=headers) as resp:
                    data = await resp.json()
                    status = data.get("status")
                    
                    if status == "succeeded":
                        output = data.get("output")
                        video_url = output if isinstance(output, str) else output[0]
                        break
                    elif status in ["failed", "canceled"]:
                        await status_msg.edit_text("❌ Videoni yaratishda xatolik yuz berdi.")
                        return

            await status_msg.delete()
            await message.answer_video(
                video=video_url,
                caption=f"✨ **Videongiz tayyor!**\n\n📌 **Prompt:** `{prompt}`",
                parse_mode="Markdown"
            )

        except Exception as e:
            await status_msg.edit_text(f"❌ Xatolik: {str(e)}")

async def main():
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
