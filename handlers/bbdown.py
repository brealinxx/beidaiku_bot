import os
from os import *
from telebot import TeleBot
from telebot.types import Message
import subprocess
import re
import asyncio
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

tg_key = environ.get("TELEGRAM_BOT_TOKEN")

def BBDown(message: Message, bot: TeleBot) -> None:  
    """BBDown : /bbdown <bilibili URL> <title>"""
    url, title = extract_url_and_title(message.text)
    download_path = os.path.expanduser("/root/videos")

    output, error = DownloadBBDVideo(url, download_path)
    print(output)
    if error:
        bot.reply_to(message, f"下载错误: {error}")
        return 

    try: 
        for file_info in list_files_details(download_path):
            print(f"Name: {file_info['name']}, Size: {file_info['size']} bytes, Last Modified: {file_info['last_modified']}")
        sorted_files_info = sorted(list_files_details(download_path), key=lambda x: x["last_modified"], reverse=True)
        # for file in os.listdir(download_path):
        #     if file.endswith(".mp4") and " " in file:
        #         new_name = file.replace(" ", "_") 
        #         old_path = os.path.join(download_path, file)
        #         new_path = os.path.join(download_path, new_name)
        #         os.rename(old_path, new_path)

        mp4_files = [file for file in os.listdir(download_path) if file.endswith(".mp4")]
        for file in mp4_files:
            #video_path = os.path.join(download_path, file)
            video_path = sorted_files_info[0]
            curl_command = [ #telegram doc
            'curl',
            '-X', 'POST', f"https://api.telegram.org/bot{tg_key}/sendVideo",
            '-H', 'User-Agent: Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)',
            '-F', f'chat_id={message.chat.id}',
            '-F', f'video=@{video_path}',
            '-F', f'caption={title}',
            '-F', 'disable_notification=false'
            ]
            subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(tg_key)
            print(message.chat.id)
            print(video_path)
            print(title)
    except Exception as e:
        bot.reply_to(
            message,
            f"发生错误: {str(e)}"
        )
    finally:
        bot.delete_message(message.chat.id, message.message_id)
        monitor_folder(download_path)

def DownloadBBDVideo(url, download_path):
    process = subprocess.Popen(['/root/DEV/BBDown', '--work-dir', download_path, url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode != 0:
        return None, error.decode('utf-8')
    return output.decode('utf-8'), None

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        video_path = event.src_path
        time.sleep(60)
        os.remove(video_path)

def monitor_folder(folder_path):
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# def HexToDec(hex_str: str) -> int:
#     dec_num = 0
#     for i, c in enumerate(hex_str):
#         dec_num += (16 ** (len(hex_str) - i - 1)) * ord(c) - ord('0')
#     return dec_num

# def GetVideoID(URL):
#     BVGroup = re.search(r"BV[0-9a-zA-Z]+", URL)
#     BV = BVGroup.group()
#     return HexToDec(BV)

def extract_url_and_title(text):
    pattern = r'(https?://\S+)\s(.+)'
    match = re.match(pattern, text)
    if match:
        url = match.group(1)
        title = match.group(2)
        return url, title
    else:
        return None, None
    
# def translate_space(title):
#     return re.sub(r"\s", r"\\ ", title)
    
# def SendVideo(chat_id, title, video_path):
#    return
    
def list_files_details(folder_path):
    try:
        files = os.listdir(folder_path)
        details = []
        for file in files:
            file_path = os.path.join(folder_path, file)
            file_stat = os.stat(file_path)
            details.append({
                
                'name': file,
                'size': file_stat.st_size,
                'last_modified': file_stat.st_mtime
            })
        return details
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        return []

def register(bot: TeleBot) -> None:
    bot.register_message_handler(BBDown, commands=["bbdown"], pass_bot=True)
    bot.register_message_handler(BBDown, regexp="^bbdown:", pass_bot=True)