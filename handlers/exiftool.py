import os
from telebot import TeleBot
from telebot.types import Message
import subprocess
import tempfile
import re

cmds = []
helpTrigger = None
transTrigger = None

def ExifHelp(message: Message, bot: TeleBot) -> None:
     '''exiftool: help'''
     extraCmd = message.text.strip()
     try:
          if extraCmd == "help":
               helpTrigger = True
               bot.reply_to(message, f"EXIF 是Exchangeable Image File 的缩写，这是一种用于使用 JPEG 压缩在数字摄影图像文件中存储交换信息的标准格式。几乎所有新型数码相机都使用 EXIF 注释，存储有关图像的信息，如快门速度、曝光补偿、光圈值、所使用的测光系统、是否使用了闪光灯、ISO 编号、拍摄日期和时间、白平衡以及所使用的辅助镜头和分辨率。有些图像甚至也会存储 GPS 信息。\n 
                            本功能需要上传图片需要以「file」的形式上传文件")
     except Exception as e:
          bot.reply_to(message, f"发生错误: {str(e)}")
          

def Exif(message: Message, bot: TeleBot) -> None:
     """exiftool : /exif --help <photo>"""
     s = message.caption
     extraCmd = s.strip()
     file_info = bot.get_file(message.document.file_id)
     file_path = file_info.file_path
     downloaded_file = bot.download_file(file_path)

     _, file_ext = os.path.splitext(file_path)
     with tempfile.NamedTemporaryFile(dir="/root/media", delete=False, suffix=file_ext) as temp_file:
          temp_file.write(downloaded_file)
          temp_file_path = temp_file.name
     print(temp_file_path)
     if extraCmd == "clean": 
          transTrigger = True
          file_data_process = subprocess.Popen(['exiftool','-alldates=', '-gps:all=', temp_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
     elif extraCmd:
          transTrigger = True
          file_data_process = subprocess.Popen(['exiftool',cmds, temp_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
     else:
          file_data_process = subprocess.Popen(['exiftool', temp_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

     stdout, stderr = file_data_process.communicate()

     send_telegram_message(bot, message, stdout, temp_file_path)

def extraCmdList(exif_data):
     pattern = re.compile(r'^-(.*?)=\s(.*?)$')
     match = pattern.finditer('-Make= -CAM= -Model= -hh=')

     for m in match:
          print(m.group(0))
          cmds.append(m.group(0))

def send_telegram_message(bot, message, stdout, tempFilePath):
    if len(stdout) <= 4096:
          output = f"<span class=\"tg-spoiler\">照片信息：\n{stdout.decode('utf-8')}</span>。"
          try:
               bot.reply_to(message, text=output, parse_mode="HTML")
          except Exception as e:
               bot.reply_to(message, f"发生错误: {str(e)}")
          finally:
               if os.path.exists(tempFilePath):
                    os.remove(tempFilePath)
    else:
        chunks = [stdout[i:i+4000] for i in range(0, len(stdout), 4000)]
        for chunk in chunks:
          try:
               bot.reply_to(message, text=output, parse_mode="HTML")
          except Exception as e:
               bot.reply_to(message, f"发生错误: {str(e)}")
          finally:
               if not transTrigger:
                    send_telegram_message(bot, message, stdout, tempFilePath)
                    transTrigger = False
               if os.path.exists(tempFilePath):
                    os.remove(tempFilePath)
                    


def register(bot: TeleBot) -> None:
     bot.register_message_handler(ExifHelp, commands=["exif"], pass_bot=True)
     bot.register_message_handler(ExifHelp, regexp="^exif:", pass_bot=True)
     if not helpTrigger:
          bot.register_message_handler(
               Exif,
               content_types=["document","photo"],
               func=lambda m: m.caption and m.caption.startswith(("exif:", "/exif")),
               pass_bot=True
          )