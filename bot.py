import telebot
from yt_dlp import YoutubeDL
import os
import re

# Get token environment variable
token = os.environ.get('SHORTS_TOKEN')
if not token:
    raise ValueError('No token specified')

bot = telebot.TeleBot(token)

# yt-dlp settings
ydl_opts = {
    'format': 'best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Hi! 👋\n"
        "I am a bot, which purpose is to help you download YT Shorts videos easily. 📺\n\n"
        "Just send me a YouTube Shorts link, and I will send back original video! 😎\n"
        "If there's multiple links, I will handle them all. 🔗\n\n"
        "Let's get started! 🚀"
    )
    bot.reply_to(message, welcome_text)

def download_youtube_shorts(url):
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info_dict)
    return file_path

@bot.message_handler(func=lambda message: 'youtube.com/shorts/' in message.text or 'youtu.be/shorts/' in message.text)
def handle_youtube_shorts(message):
    urls = re.findall(r'(https?://(?:www\.)?(?:youtube\.com/shorts/|youtu\.be/shorts/)\S+)', message.text)
    if not urls:
        bot.reply_to(message, 'No YouTube Shorts links found.')
        return
    unique_urls = list(set(urls))  # Killing duplicates
    download_msg = bot.reply_to(message, 'Downloading... 🕐')
    for url in unique_urls:
        try:
            video_path = download_youtube_shorts(url)
            with open(video_path, 'rb') as video:
                bot.send_video(message.chat.id, video)
            os.remove(video_path)  # Deleting video after sending
        except Exception as e:
            bot.reply_to(message, f'There is an issue: {e}')
    bot.delete_message(message.chat.id, download_msg.message_id)

# Bot listening
bot.polling(none_stop=True)
