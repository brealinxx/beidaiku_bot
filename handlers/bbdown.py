import os
from os import *
from telebot import TeleBot
from telebot.types import Message
import subprocess
import re
import time

tg_key = environ.get("TELEGRAM_BOT_TOKEN")

def BBDown(message: Message, bot: TeleBot) -> None:  
    """BBDown : /bbdown <bilibili URL>"""
    download_path = os.path.expanduser("/root/videos")
    url = extract_url_and_title(message.text)
    
    output, error = DownloadBBDVideo(url, download_path)
    if error:
        bot.reply_to(message, f"下载错误: {error}")
        return 

    try: 
        for file_info in list_files_details(download_path):
            print(f"Name: {file_info['name']}, Size: {file_info['size']} bytes, Path: {file_info['path']}, Last Modified: {file_info['last_modified']}")
        sorted_files_info = sorted(list_files_details(download_path), key=lambda x: x["last_modified"], reverse=True)
        if sorted_files_info:
            video_path = sorted_files_info[0]["path"]
            title = sorted_files_info[0]["name"]
            print(video_path)
        else:
            print("文件信息列表为空")
        curl_command = [ #telegram doc
        'curl',
        '-X', 'POST', f"https://api.telegram.org/bot{tg_key}/sendVideo",
        '-H', 'User-Agent: Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)',
        '-F', f'chat_id={message.chat.id}',
        '-F', f'video=@{video_path}',
        '-F', f"caption='@{bot.get_chat(message.chat.id).username}' 下载成功！\n{title}",
        '-F', 'disable_notification=false',
        ]
        downloadingMeg = bot.reply_to(message, "正在下载 请稍后 QaQ",)
        subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        bot.reply_to(
            message,
            f"发生错误: {str(e)}"
        )
    finally:
        time.sleep(60)
        os.remove(video_path)
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(downloadingMeg.chat.id, downloadingMeg.message_id)

def DownloadBBDVideo(url, download_path):
    process = subprocess.Popen(['/root/DEV/BBDown', '--work-dir', download_path, url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode != 0:
        return None, error.decode('utf-8')
    return output.decode('utf-8'), None

# def HexToDec(hex_str: str) -> int:
#     dec_num = 0
#     for i, c in enumerate(hex_str):
#         dec_num += (16 ** (len(hex_str) - i - 1)) * ord(c) - ord('0')
#     return dec_num

def extract_url_and_title(text):
    pattern = r'https://www.bilibili.com/video/[^/?]*' #'(https?://\S+)\s(.+)'
    match = re.match(pattern, text)
    if match:
        url = match.group(1)
        return url
    else:
        return None
    
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
                'path': file_path,
                'last_modified': file_stat.st_mtime
            })
        return details
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        return []

def register(bot: TeleBot) -> None:
    bot.register_message_handler(BBDown, commands=["bbdown"], pass_bot=True)
    bot.register_message_handler(BBDown, regexp="^bbdown:", pass_bot=True)