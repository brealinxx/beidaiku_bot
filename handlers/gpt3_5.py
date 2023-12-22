import requests
from os import environ
from telebot import TeleBot
from telebot.types import Message
import json

#OPENAI_GPT_3_5_KEY = environ.get("GOOGLE_GEMINI_KEY")
gpt3_5_key = ''

def gpt3_5_handler(message: Message, bot: TeleBot) -> None:  
    """OpenAI : /gpt3.5 <question>"""
    url = 'https://api.chatanywhere.com.cn/v1/chat/completions'
    reply_message = bot.reply_to(
        message,
        "Generating OpenAI GPT3.5 answer please wait, note, will only keep the last five messages:",
    )
    m = message.text.strip()
    # data = {
    #     "prompt": {
    #         "text": f"{m}"
    #     }
    # }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {gpt3_5_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": f"{m}"}],
    }
    response = requests.post(url, headers=headers, json=data)

    try:
        if 'choices' in response.json() and len(response.json()['choices']) > 0:
            output = response.json()['choices'][0]['message']['content']
        
        bot.reply_to(
            message,
            "GPT3.5 answer:\n" + output,
        )
    except:
        bot.reply_to(
            message,
            "An error occurred while processing the request.",
        )
    finally:
        bot.delete_message(reply_message.chat.id, reply_message.message_id)

def register(bot: TeleBot) -> None:
    bot.register_message_handler(gpt3_5_handler, commands=["gpt3d5"], pass_bot=True)
    bot.register_message_handler(gpt3_5_handler, regexp="^gpt3d5:", pass_bot=True)