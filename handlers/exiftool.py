import os
from os import *
from telebot import TeleBot
from telebot.types import Message
import subprocess
import re
from pathlib import Path

def Exif(message: Message, bot: TeleBot) -> None:  
     """exiftool : /exif <photo>"""
 
     try:
          max_size_photo = max(message.photo, key=lambda p: p.file_size)
          file_path = bot.get_file(max_size_photo.file_id).file_path
          downloaded_file = bot.download_file(file_path)
          with open("photo_temp.jpg", "wb") as temp_file:
               temp_file.write(downloaded_file)
          image_path = Path("photo_temp.jpg")
          image_data = image_path.read_bytes()

          photo_data_process = subprocess.Popen(['exiftool', image_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          stdout, stderr = photo_data_process.communicate()
        
          bot.reply_to(
               message,
               f"照片信息:\n {stdout.decode('utf-8')}"
          )
     except Exception as e:
          bot.reply_to(
               message,
               f"发生错误: {str(e)}"
          )
     finally:print()
    

def register(bot: TeleBot) -> None:
     bot.register_message_handler(Exif, commands=["exif"], pass_bot=True)
     bot.register_message_handler(Exif, regexp="^exif:", pass_bot=True)