import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from src.search import search
from src.video_utils import create_clip, concat_clips


load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
VIDEO_PATH = "data/videos/video1.mp4"
TEMP_DIR = Path("data/temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я могу помочь найти кусок видео по описанию.\n"
        "Напиши фразу или слово, например: family, beach sunset, camping, christmas dinner.\n"
        "Если хочешь, я могу показать примеры запросов, напиши /examples"
    )

async def examples(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Примеры запросов:\n\n"
        "beach sunset\n"
        "people on the beach\n"
        "camping in forest\n"
        "campfire\n"
        "family with baby\n"
        "cooking in kitchen\n"
        "christmas celebration\n"
        "city street crossing\n"
        "family walking outdoors\n"
        "dog in nature\n"
        "exercising at home"
    )


async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text

    await update.message.reply_text("Уже ищу видосик...")

    results = search(query, top_k=3)

    if not results:
        await update.message.reply_text("Я пока не сильно умненькая, поэтому ничего не смогла найти на ваш запрос.. Попробуйте /examples")
        return
    
    results_text = f"🔍 Query: {query}\n\n"

    for i, result in enumerate(results, 1):
        results_text += (
            f"{i}. {result['timestamp']} | "
            f"{result['score']:.2f}\n"
            f"{result['description']}\n\n"
        )
    await update.message.reply_text(results_text)

    run_id = uuid.uuid4().hex[:8]

    clip_paths = []

    for i, result in enumerate(results, 1):
        timestamp_sec = result.get("timestamp_sec")

        if timestamp_sec is None:
            continue

        clip_path = TEMP_DIR / f"{run_id}_clip_{i}.mp4"

        create_clip(
            video_path=VIDEO_PATH,
            center_sec=float(timestamp_sec),
            output_path=str(clip_path),
            clip_duration=6,
        )

        clip_paths.append(str(clip_path))

    if not clip_paths:
        await update.message.reply_text(
            "Нашла результаты, но не смогла вырезать видео: нет timestamp_sec."
        )
        return

    result_video_path = TEMP_DIR / f"{run_id}_result.mp4"

    concat_clips(
        clip_paths=clip_paths,
        output_path=str(result_video_path),
    )

    best = results[0]

    if best.get("score", 0) < 0.1:
        await update.message.reply_text(
            "Я не нашла подходящий кадр"
            "Попробуй другой запрос, например:\n"
            "beach sunset\n"
            "family cooking\n"
            "camping\n"
            "christmas dinner\n"
            "people crossing street\n"
            "family walking with dog"
        )
        return

    caption = (
        f"Top-3 moments for: {query}\n\n"
        f"Best match:\n"
        f"Timestamp: {best.get('timestamp')}\n"
        f"Score: {best.get('score'):.3f}\n"
        f"Description: {best.get('description')}"
    )

    

    with open(result_video_path, "rb") as video:
        await update.message.reply_video(
            video=video,
            caption=caption,
        )


def main():
    if not BOT_TOKEN:
        raise ValueError("Set TELEGRAM_BOT_TOKEN environment variable")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("examples", examples))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()