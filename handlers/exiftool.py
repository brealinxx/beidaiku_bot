import os
from telebot import TeleBot
from telebot.types import Message
import subprocess
import tempfile
import re

cmds = []
helpTrigger = None

def Exif(message: Message, bot: TeleBot) -> None:
     """exiftool : /exif [help] or <photoFile>"""
     s = message.caption
     extraCmd = s.strip()
     file_info = bot.get_file(message.document.file_id)
     file_path = file_info.file_path
     downloaded_file = bot.download_file(file_path)

     _, file_ext = os.path.splitext(file_path)
     with tempfile.NamedTemporaryFile(dir="/root/media", delete=False, suffix=file_ext) as temp_file:
          temp_file.write(downloaded_file)
          temp_file_path = temp_file.name
     
     extraCmdList(extraCmd)
     send_telegram_message(bot, message, get_stdout(bot, message, extraCmd, temp_file_path), temp_file_path)

def ExifHelp(message: Message, bot: TeleBot) -> None:
     '''exiftool: help'''
     extraCmd = message.text.strip()
     try:
          if extraCmd == "help":
               helpTrigger = True
               bot.reply_to(message, f"EXIF 是Exchangeable Image File 的缩写，这是一种用于使用 JPEG 压缩在数字摄影图像文件中存储交换信息的标准格式。几乎所有新型数码相机都使用 EXIF 注释，存储有关图像的信息，如快门速度、曝光补偿、光圈值、所使用的测光系统、是否使用了闪光灯、ISO 编号、拍摄日期和时间、白平衡以及所使用的辅助镜头和分辨率。有些图像甚至也会存储 GPS 信息。"+ 
                            "\n本功能上传的图片需要以「file」的形式上传")
     except Exception as e:
          bot.reply_to(message, f"发生错误: {str(e)}")

def get_stdout(bot, message, extraCmd, tempFilePath):
    try:
        if extraCmd == "clean":
            clean_process = subprocess.Popen(['exiftool','-alldates=', '-gps:all=', tempFilePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = clean_process.communicate()
            if clean_process.returncode != 0:
                print(f"Error in cleaning process: {stderr}")
                return stdout

            send_cleaned_file(bot, message, tempFilePath)
            file_data_process = subprocess.Popen(['exiftool', '-a', '-u', '-g1', tempFilePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = file_data_process.communicate()
            if file_data_process.returncode != 0:
                print(f"Error in file data reading process: {stderr}")
        elif extraCmd:
            for cmd in cmds:
                print(cmd)
                reWrite_process = subprocess.Popen(['exiftool', cmd, tempFilePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = reWrite_process.communicate()
                if reWrite_process.returncode != 0:
                    print(f"Error in rewrite process: {stderr}")
                    return stdout
        else:
            file_data_process = subprocess.Popen(['exiftool', '-a', '-u', '-g1', tempFilePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = file_data_process.communicate()
            if file_data_process.returncode != 0:
                print(f"Error in file data process: {stderr}")

    except Exception as e:
        bot.reply_to(message, f"发生错误: {str(e)}")
        return None

    return stdout

def send_telegram_message(bot, message, stdout, tempFilePath):
     if len(stdout) <= 4096:
          try:
               bot.reply_to(message, text=output_result(stdout), parse_mode="HTML")
          except Exception as e:
               bot.reply_to(message, f"发生错误: {str(e)}")
          finally:
               if os.path.exists(tempFilePath):
                    os.remove(tempFilePath)
     else:
        chunks = [stdout[i:i+4000] for i in range(0, len(stdout), 4000)]
        for chunk in chunks:
          try:
               bot.reply_to(message, text=output_result(chunk), parse_mode="HTML")
          except Exception as e:
               bot.reply_to(message, f"发生错误: {str(e)}")
          finally:
               if os.path.exists(tempFilePath):
                    os.remove(tempFilePath)

def send_cleaned_file(bot, message, filePath):
    try:
        with open(filePath, 'rb') as file:
            bot.send_document(message.chat.id, file)
    except Exception as e:
        bot.reply_to(message, f"发送清理后的文件时发生错误: {str(e)}")

def extraCmdList(exif_data):
     pattern = re.compile(r'^-(.*?)=\s(.*?)$')
     match = pattern.finditer(exif_data)

     for m in match:
          print(m.group(0))
          cmds.append(m.group(0))
                
def output_result(message):
     return f"<span class=\"tg-spoiler\">照片信息：\n{message.decode('utf-8')}</span>"

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