#in this module markup menus are defined for messages
import telebot
from telebot import types

class IGT_Markup(object):

#Markup for start message
    @staticmethod
    def getWelcomeAdminMarkup():
        
        markup = telebot.types.InlineKeyboardMarkup()
 
        markup.row(telebot.types.InlineKeyboardButton("welcome", callback_data='welcome_admin_CB'))
        
           
        return markup
    
    @staticmethod
    def getWelcomeUserMarkup():
        
        markup = telebot.types.InlineKeyboardMarkup()
 
        markup.row(telebot.types.InlineKeyboardButton("Теория", callback_data='Theory_CB'))
        markup.row(telebot.types.InlineKeyboardButton("Тестирование", callback_data='Practice_CB'))
        markup.row(telebot.types.InlineKeyboardButton("Текущий статус", callback_data='getStatistics'))
           
        return markup
    
    @staticmethod
    def getTheoryMarkup():
        
        markup = telebot.types.InlineKeyboardMarkup()
 
        
        markup.row(telebot.types.InlineKeyboardButton("Тестирование", callback_data='Practice_CB'))
        
           
        return markup
    
    

    @staticmethod
    def getStartQuiz():
        
        markup = telebot.types.InlineKeyboardMarkup()
 
        
        markup.row(telebot.types.InlineKeyboardButton("Текущий статус", callback_data='getStatistics'))
        markup.row(telebot.types.InlineKeyboardButton("<- Назад", callback_data='Main_Menu_CB'))
           
        return markup 
    @staticmethod
    def getPracticeMarkup():
        
        markup = telebot.types.InlineKeyboardMarkup()
 
        
        markup.row(telebot.types.InlineKeyboardButton("Junior", callback_data='Practice_test_junior_CB'))
        markup.row(telebot.types.InlineKeyboardButton("Middle", callback_data='Practice_test_middle_CB'))
        markup.row(telebot.types.InlineKeyboardButton("Senior", callback_data='Practice_test_senior_CB'))
        markup.row(telebot.types.InlineKeyboardButton("<- Назад", callback_data='Main_Menu_CB'))

        return markup