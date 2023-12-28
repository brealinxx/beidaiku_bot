from telebot import *
from telebot.types import Message
import google.generativeai as genai
import requests
from os import environ

# proxies = {
#     'http': 'http://127.0.0.1:7890',
#     'https': 'http://127.0.0.1:7890'
# }
# response = requests.get('https://api.telegram.org/bot<YourBotToken>/getMe', proxies=proxies)

TELEGRAM_API_KEY = environ.get("Telegram_Bot_Token")
TELEGRAM_API_KEY = ''
GOOGLE_GEMINI_KEY = environ.get("Google_Gemini_API_Key")

#bot = telebot.TeleBot(TELEGRAM_API_KEY)

genai.configure(api_key=GOOGLE_GEMINI_KEY)
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

gemini_player_dict = {}

def make_new_gemini_convo():
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    convo = model.start_chat()
    return convo

def gemini_handler(message: Message, bot: TeleBot) -> None:
    """Gemini : /gemini <question>"""
    reply_message = bot.reply_to(
        message,
        "Generating google gemini answer please wait, note, will only keep the last five messages:",
    )
    m = message.text.strip()
    player = None
 
    if str(message.from_user.id) not in gemini_player_dict:
        player = make_new_gemini_convo()
        gemini_player_dict[str(message.from_user.id)] = player
    else:
        player = gemini_player_dict[str(message.from_user.id)]
    if len(player.history) > 10:
        player.history = player.history[2:]
    player.send_message(m)
    try:
        bot.reply_to(
            message,
            "Gemini answer:\n" + player.last.text,
            parse_mode="MarkdownV2",
        )
    except:
        bot.reply_to(
            message,
            "Gemini answer:\n" + player.last.text,
        )
    finally:
        bot.delete_message(reply_message.chat.id, reply_message.message_id)

def register(bot: TeleBot) -> None:
    bot.register_message_handler(gemini_handler, commands=["gemini"], pass_bot=True)
    bot.register_message_handler(gemini_handler, regexp="^gemini:", pass_bot=True)
#     bot.register_message_handler(
#         gemini_photo_handler,
#         content_types=["photo"],
#         func=lambda m: m.caption and m.caption.startswith(("gemini:", "/gemini")),
#         pass_bot=True,
#     )


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "这里是最伟大的背带裤！")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "你可以在这里输入你需要的帮助信息。")

@bot.message_handler(commands=['clear'])
def clear_chat(message):
    # 获取消息的 chat_id
    chat_id = message.chat.id
    # 发送空消息来清空聊天记录
    bot.send_chat_action(chat_id, 'typing')  
    bot.send_message(chat_id, "Chat has been cleared.")



bot.polling()