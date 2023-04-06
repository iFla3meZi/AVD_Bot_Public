import logging
import asyncio
import os
import yt_dlp as youtube_dl
from yt_dlp import YoutubeDL
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

API_TOKEN = 'your_api_token_here'

# Initialization of the board and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Creating a list with tasks for a queue
download_queue = []


# Handler of the /start command
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
# Welcome message when using the /start command
    await message.reply("Hi! Send me a link to a YouTube video and I'll help you download it.")


# Text Message Handler (for YouTube links)
@dp.message_handler()
async def process_link(message: types.Message):
# Processing links to YouTube videos, providing a choice of format and adding a task to the queue
    url = message.text
    chat_id = message.chat.id  # Chat_id definition
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

    except Exception as e:
        await message.reply("Error processing the link. Make sure the link is correct.")
        return
    
    # Creating buttons for format selection
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Audio", callback_data=f"audio|{message.chat.id}|{url}"))
    markup.add(types.InlineKeyboardButton("Video", callback_data=f"video|{message.chat.id}|{url}"))

    logging.info("Sending message with format options")

    await bot.send_message(
        chat_id=chat_id,
        text="Select the file format:",
        reply_markup=markup,  # Correction of the variable name
    )

    logging.info("Message with format options sent")

# Function for deleting old service messages
async def delete_previous_message(chat_id, message_id):
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"Error deleting a message: {str(e)}")


# Format Selection Handler
@dp.callback_query_handler(lambda c: c.data.startswith('audio') or c.data.startswith('video'))
async def process_format_choice(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    format_type, user_id, url = call.data.split("|")

    # New queue item with information about chat_id, url and selected format
    queue_item = {
        'chat_id': call.message.chat.id,
        'url': url,
        'format': format_type
    }

    # Adding an item to the queue
    download_queue.append(queue_item)

    # Notification to the user about adding a task to the queue and its position
    position = len(download_queue)
    await bot.send_message(chat_id=call.message.chat.id, text=f"The request has been added to the queue. Your position: {position}.")

    audio_ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    video_ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    if format_type == 'audio':
        ydl_opts = audio_ydl_opts
    elif format_type == 'video':
        ydl_opts = video_ydl_opts

    chat_id = call.message.chat.id
    await bot.send_chat_action(chat_id, action="typing")

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        temp_file_title = ydl.prepare_filename(info_dict)
    if format_type == 'audio':
        file_title = temp_file_title.replace('.webm', '.mp3')
    else:
        file_title = temp_file_title
    try:
        await call.message.answer(f"Скачиваю {format_type}...")
        ydl.download([url])

        with open(file_title, 'rb') as f:
            if format_type == 'audio':
                sent_message = await call.message.answer_audio(f, title=file_title)
            elif format_type == 'video':
                sent_message = await call.message.answer_video(f, caption=file_title)

        os.remove(file_title)
        await delete_previous_message(chat_id, call.message.message_id)
    except Exception as e:
        await call.message.answer(f"Error when downloading a file: {str(e)}")
        logging.exception(f"Error when downloading a file: {str(e)}")

# Asynchronous queue processing
async def process_queue():
    while len(download_queue) > 0:
        current_item = download_queue.pop(0)
        chat_id = current_item["chat_id"]
        url = current_item["url"]
        file_format = current_item["format"]

        ydl_opts = {
            'quiet': True,
            'skip_download': False,
            'format': 'bestaudio/best' if file_format == "audio" else 'best',
            'outtmpl': f'downloads/{chat_id}/%(title)s.%(ext)s',
            'ignore_config': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)

        # Sending the downloaded file
        try:
            with open(file_path, 'rb') as file:
                if file_format == "audio":
                    await bot.send_audio(chat_id, audio=file)
                elif file_format == "video":
                    await bot.send_video(chat_id, video=file)
        except Exception as e:
            await bot.send_message(chat_id, f"Error sending file: {e}")

        # Deleting a file after sending
        try:
            os.remove(file_path)
        except Exception as e:
            await bot.send_message(chat_id, f"Error deleting a file: {e}")

        # Delay between processing items in the queue (optional)
        await asyncio.sleep(1)

# Start
async def on_startup(dp):
    await bot.send_message(chat_id=YOUR_ID, text="The bot has started")
    asyncio.create_task(process_queue())

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)