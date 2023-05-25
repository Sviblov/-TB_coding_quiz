#Telegram Bot

import logging
import os




import telebot

#importing handlers
from modules.handlers.user import welcome_command_user, any_message_user, get_user_statistics, Theory_callback, handle_poll_answer, Practice_callback, send_questionaire_callback




#DB connection and Markup setup

from modules.utils.IGT_Mongo import Database




# creating bot

if os.environ.get('DEBUG')=='1':
    bottoken = os.environ.get('BOT_KEY_DEV')
    bot = telebot.TeleBot(os.environ.get('BOT_KEY_DEV'))
    DB_name = 'Coding_Quiz_Database'
    DB=Database(URL = os.environ.get('CODING_QUIZ_BOT_DB'),database =DB_name)
    loggingLevel = logging.INFO

else:
    DB=Database()
    DBTaskScheduler=Database()
    bottoken = os.environ.get('BOT_KEY')
    bot = telebot.TeleBot(os.environ.get('BOT_KEY'))
    loggingLevel = logging.INFO

#starting mongoDB connection
#Logging setup
logging.basicConfig(handlers=[logging.StreamHandler()], encoding='utf-8', level=loggingLevel, format=' %(asctime)s - %(levelname)s - %(message)s')




DB.openConnection()
standardMessages = DB.getStandardMessages()
bot.db_connection = DB
bot.token=bottoken




def registerHandlers():
     
    bot.register_message_handler(welcome_command_user, commands=['start'], pass_bot='True')
    bot.register_message_handler(any_message_user, func=lambda message: True, pass_bot='True')
    

    bot.register_callback_query_handler(Theory_callback,func=lambda call: 'Theory_CB' in call.data, pass_bot=True)
    bot.register_callback_query_handler(Practice_callback,func=lambda call: 'Practice_CB' in call.data, pass_bot=True)
    bot.register_callback_query_handler(send_questionaire_callback,func=lambda call: 'Practice_test_' in call.data, pass_bot=True)
    bot.register_callback_query_handler(welcome_command_user,func=lambda call: 'Main_Menu_CB' in call.data, pass_bot=True)
    bot.register_callback_query_handler(get_user_statistics,func=lambda call: 'getStatistics' in call.data, pass_bot=True)
    


    bot.register_poll_answer_handler(handle_poll_answer, func=lambda pollAnswer: True, pass_bot=True)
    

    #bot.register_message_handler(all_messages_handler, func=lambda pollAnswer: True, pass_bot=True, isSubscribed=True)

registerHandlers()


        

while True:
    try:
        logging.info('Starting Bot Polling...')
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f'Bot restarted after the error. Error: {e}')
