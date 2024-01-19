import os
from telebot import TeleBot
from telebot.types import Message
import subprocess
from pathlib import Path
import tempfile
import re

cmds = []

def Exif(message: Message, bot: TeleBot) -> None:
     """exiftool : /exif --help <photo>"""
     s = message.caption
     extraCmd = s.strip()
     max_size_photo = max(message.photo, key=lambda p: p.file_size)
     file_info = bot.get_file(max_size_photo.file_id)
     file_path = file_info.file_path
     downloaded_file = bot.download_file(file_path)

     _, file_ext = os.path.splitext(file_path)
     with tempfile.NamedTemporaryFile(dir="/root/media", delete=False, suffix=file_ext) as temp_file:
          temp_file.write(downloaded_file)
          temp_file_path = temp_file.name

     if extraCmd is "help":
          bot.reply_to(message, f"EXIF 是Exchangeable Image File 的缩写，这是一种用于使用 JPEG 压缩在数字摄影图像文件中存储交换信息的标准格式。几乎所有新型数码相机都使用 EXIF 注释，存储有关图像的信息，如快门速度、曝光补偿、光圈值、所使用的测光系统、是否使用了闪光灯、ISO 编号、拍摄日期和时间、白平衡以及所使用的辅助镜头和分辨率。有些图像甚至也会存储 GPS 信息。")
     elif extraCmd is "clean": 
          photo_data_process = subprocess.Popen(['exiftool','-alldates=', '-gps:all=', temp_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
     elif extraCmd:
          photo_data_process = subprocess.Popen(['exiftool',cmds, temp_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
     else:
          photo_data_process = subprocess.Popen(['exiftool', temp_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

     stdout, stderr = photo_data_process.communicate()

     try:
          bot.reply_to(message, f"照片信息:\n {stdout.decode('utf-8')}")

     except Exception as e:
          bot.reply_to(message, f"发生错误: {str(e)}")

     finally:
          if os.path.exists(temp_file_path):
               os.remove(temp_file_path)

def extraCmdList(exif_data):
     pattern = re.compile(r'^-(.*?)=\s(.*?)$')
     match = pattern.finditer('-Make= -CAM= -Model= -hh=')

     for m in match:
          print(m.group(0))
          cmds.append(m.group(0))


def register(bot: TeleBot) -> None:
     bot.register_message_handler(Exif, commands=["exif"], pass_bot=True)
     bot.register_message_handler(Exif, regexp="^exif:", pass_bot=True)
     bot.register_message_handler(
          Exif,
          content_types=["photo"],
          func=lambda m: m.caption and m.caption.startswith(("exif:", "/exif")),
          pass_bot=True
     )