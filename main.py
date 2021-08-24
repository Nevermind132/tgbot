import config
import csv
import telebot
import requests
import dbworker
from bs4 import BeautifulSoup as BS
from telebot import types

bot = telebot.TeleBot(config.TOKEN)

urls=[]

headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
}

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Для работы напишите /check")

@bot.message_handler(commands=["addtarget"])
def addtarget(message):
    bot.send_message(message.chat.id, "Напишите ID цели")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_URL.value)
    
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_URL.value)
def user_entering_url(message):
    bot.send_message(message.chat.id, "URL сохранился!")
    global urls
    urls.append(message.text)
    dbworker.set_state(message.chat.id, config.States.S_START.value)


@bot.message_handler(commands=["check"])
def check(message):
    global urls
    names={}
    status_list={}
    i=0
    s=' '
    for i in range(len(urls)):  
        html=requests.get(urls[i],headers=headers).text
        parsed=BS(html,'html.parser')   
        name = parsed.find('h1', {'class': 'page_name'}).text
        status = parsed.find('span',{'class':'current_text'}).text
        names[i]=name
        status_list[i]=status
    for i in range(len(urls)):
        s+=("ID пользователя : " + urls[i] + '\n' + "Имя пользователя : " + names[i] + '\n' + "Статус : " + status_list[i] + '\n\n')
    bot.send_message(chat_id=config.chat_id,text=s)


if __name__ =='__main__':
    bot.polling(none_stop=True)
