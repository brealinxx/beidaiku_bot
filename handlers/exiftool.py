import os
from telebot import TeleBot
from telebot.types import Message
import subprocess
from pathlib import Path
import tempfile

def Exif(message: Message, bot: TeleBot) -> None:
    """exiftool : /exif <photo>"""
    try:
        max_size_photo = max(message.photo, key=lambda p: p.file_size)
        file_info = bot.get_file(max_size_photo.file_id)
        file_path = file_info.file_path
        downloaded_file = bot.download_file(file_path)

        _, file_ext = os.path.splitext(file_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(downloaded_file)
            temp_file_path = temp_file.name

        photo_data_process = subprocess.Popen(['exiftool', temp_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = photo_data_process.communicate()

        bot.reply_to(message, f"照片信息:\n {stdout.decode('utf-8')}")

    except Exception as e:
        bot.reply_to(message, f"发生错误: {str(e)}")

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def register(bot: TeleBot) -> None:
    bot.register_message_handler(Exif, commands=["exif"], pass_bot=True)
    bot.register_message_handler(Exif, regexp="^exif:", pass_bot=True)