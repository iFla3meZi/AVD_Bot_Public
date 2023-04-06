# 🎬 YouTube Downloader Bot
This project is a Telegram bot for downloading audio and video files from YouTube.

# 🚀 Getting Started
These instructions will help you set up and run the YouTube Downloader Bot on your machine.

## Prerequisites
Make sure you have Python 3.7 or higher installed. You can check your Python version by running:
```
python --version
```
## Installation
1. Clone the repository to your computer:
```
git clone https://github.com/yourusername/your-repo-name.git
```
2. Install the required dependencies:
```python
pip install -r requirements.txt
```

# 🛠 Configuration
1. Create a new bot via BotFather on Telegram and obtain your API token.
2. Open the main.py file and replace API_TOKEN with your API token:
```python
API_TOKEN = 'your_api_token_here'
```
3. Also don't forget to replace the ID in the chat_id function:
```python
# Start
async def on_startup(dp):
    await bot.send_message(chat_id=YOUR_ID, text="The bot has started")
    asyncio.create_task(process_queue())
```

# 🎉 Usage
Run the bot using the following command:
```
python main.py
```
The bot should now be active and ready to use. Send a YouTube video link to the bot in a chat, and it will provide you with options to download the audio or video file.

# 📚 Additional Information
You can control the bot using the following commands:
```
/start: Starts the bot and displays a welcome message.
```
To download a file, send a YouTube video URL to the bot. It will then offer you the option to download the file in either audio or video format. Select your preferred format, and the bot will process your request and send you the file.
