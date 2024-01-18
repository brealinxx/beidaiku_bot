import os
from telebot import TeleBot
from telebot.types import Message
import subprocess
from pathlib import Path
import tempfile

def Exif(message: Message, bot: TeleBot) -> None:
     """exiftool : /exif <photo>"""
     print("1")
     print(message.photo[0])
     max_size_photo = max(message.photo, key=lambda p: p.file_size)
     print("2")
     file_info = bot.get_file(message.photo.file_id)
     print("3")
     file_path = file_info.file_path
     print("4")
     downloaded_file = bot.download_file(file_path)
     print("5")

     _, file_ext = os.path.splitext(file_path)
     print(file_ext)
     with tempfile.NamedTemporaryFile(dir="/root/media", delete=False, suffix=file_ext) as temp_file:
          temp_file.write(downloaded_file)
          temp_file_path = temp_file.name

     photo_data_process = subprocess.Popen(['exiftool', temp_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
     stdout, stderr = photo_data_process.communicate()
     try:
          bot.reply_to(message, f"照片信息:\n {stdout.decode('utf-8')}")

     except Exception as e:
          bot.reply_to(message, f"发生错误: {str(e)}")

     finally:
          if os.path.exists(temp_file_path):
               os.remove(temp_file_path)

def register(bot: TeleBot) -> None:
     bot.register_message_handler(
          Exif,
          content_types=["photo"],
          commands=["exif"],
          pass_bot=True
     )
     bot.register_message_handler(
          Exif,
          content_types=["photo"],
          regexp="^exif",
          pass_bot=True
     )