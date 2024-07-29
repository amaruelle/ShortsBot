import random
import re
import string
import subprocess
import requests
import telebot
import os

# Get token environment variable
token = os.environ.get('SHORTS_TOKEN')
if not token:
    raise ValueError('No token specified')

bot = telebot.TeleBot(token)


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


def get_direct_video_url(url):
    api_endpoint = "https://api.cobalt.tools/api/json"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        "url": url
    }
    response = requests.post(api_endpoint, headers=headers, json=data)
    result = response.json()
    return result["url"]


def download_video_curl(url, output_filename):
    command = ['curl', '-L', url, '-o', output_filename]
    print(f"Running command: {''.join(command)}")
    subprocess.run(command, check=True)


def generate_random_filename(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length)) + '.mp4'


@bot.message_handler(func=lambda message: any(x in message.text for x in [
                     'youtube.com/shorts/', 'youtu.be/shorts/', 'tiktok.com/', 'instagram.com/reel/', 'twitter.com/']))
def handle_message(message):
    urls = re.findall(
        r'(https?://(?:www\.)?(?:youtube\.com/shorts/|youtu\.be/shorts/|tiktok\.com/|instagram\.com/reel/|twitter\.com/[^/]+/status/)\S+)',
        message.text)
    if not urls:
        bot.reply_to(message, 'No video links found.')
        return
    unique_urls = list(set(urls))
    for url in unique_urls:
        try:
            print(f"Final URL: https://api.cobalt.tools/api/json?url={url}")
            direct = get_direct_video_url(url)
            filename = generate_random_filename()
            download_video_curl(direct, filename)
            with open(filename, 'rb') as video:
                bot.send_video(message.chat.id, video)
            os.remove(filename)
        except Exception as e:
            bot.reply_to(message, f"There is an issue: {e}")


try:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
except (ConnectionError, ReadTimeout) as e:
    sys.stdout.flush()
    os.execv(sys.argv[0], sys.argv)
else:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
