from telebot import TeleBot
from telebot.types import Message, CallbackQuery, PollAnswer
from modules.utils.IGT_Mongo import Database, noRecommendationsForThisQuestionaire
from modules.utils.IGT_Markup import IGT_Markup
import logging
from time import time
import json
import jsonpickle
from datetime import datetime, timedelta
import os
from telebot.types import InputFile



def any_message_user(message: Message, bot: TeleBot):
    
    userId=message.from_user.id
    userName=message.from_user.full_name

    replyText = message.text + "\n\n You are NOT admin"
    replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    
    logging.info(f"Echo message: username: {userName}, userId: {userId}, message: {message.text}")



def welcome_command_user(message: Message, bot: TeleBot):
   
    
    if isinstance(message, CallbackQuery):   
        from_user=message.from_user
        message = message.message
        
    else:
        from_user=message.from_user

    DB: Database = bot.db_connection
    DB.setUserToDefault(from_user)
    
    #DB.clearScheduledMessagesForUser(message.from_user)
    
   
    replyText = DB.standardMessages['startNotAdmin']
    replyMarkup = IGT_Markup.getWelcomeUserMarkup()
   
    replyMessage = bot.send_message(message.chat.id, replyText,reply_markup=replyMarkup, parse_mode='html', disable_web_page_preview=True)
    logging.info(f"Start message: username: {message.from_user.first_name}, userId: {message.from_user.id}, message: {message.text}")



def Practice_callback(callBack: CallbackQuery, bot: TeleBot):
   
    DB: Database = bot.db_connection

    replyText=DB.standardMessages['practiceCB']
    replyMarkup=IGT_Markup.getPracticeMarkup()

    bot.send_message(callBack.message.chat.id, replyText,reply_markup=replyMarkup, parse_mode='html', disable_web_page_preview=True)
    logging.info(f"Start message: username: {callBack.from_user.first_name}, userId: {callBack.from_user.id}, message: {callBack.data}")



def Theory_callback(callBack: CallbackQuery, bot: TeleBot):
   
    DB: Database = bot.db_connection

    replyText=DB.standardMessages['theoryCB']
    replyMarkup=IGT_Markup.getTheoryMarkup()

    bot.send_document(callBack.message.chat.id, InputFile('staticfiles/doc/Theory.pdf'))
    bot.send_message(callBack.message.chat.id, replyText,reply_markup=replyMarkup, parse_mode='html', disable_web_page_preview=True)
    logging.info(f"Start message: username: {callBack.from_user.first_name}, userId: {callBack.from_user.id}, message: {callBack.data}")



def send_questionaire_callback(callBack: CallbackQuery, bot: TeleBot):
   
    DB: Database = bot.db_connection

    quizDifficulty=callBack.data.split('_')[2]

    replyText=DB.standardMessages['startQuiz']
    replyMarkup=IGT_Markup.getStartQuiz()
    questions = DB.getQuestions(quizDifficulty)

    DB.increaseNumberOfTries(callBack.from_user.id, quizDifficulty)
    

    sentPolls=[]
    sentPollsId=""
    for question in questions:
        if question['questionType']=='text' or question['questionType']=='textCode':
            questionText=question['questionText']
            correctAnswer=question['correctAnser']
            answers=question['answers']
            questionType=question['questionType']
            if questionType=='textCode':
                questionCode=question['questionCode']
                bot.send_message(callBack.message.chat.id, questionCode, parse_mode='html', disable_web_page_preview=True)
    
            #bot.send_message(callBack.message.chat.id, questionText, parse_mode='html', disable_web_page_preview=True)
            poll=bot.send_poll(callBack.message.chat.id,questionText, is_anonymous=False, options = answers, open_period=600, type="quiz", correct_option_id=correctAnswer)
            
            sentPollsId=sentPollsId+poll.poll.id+"_"
            sentPolls.append({
                'id': poll.poll.id,
                'correctOptionId': correctAnswer,
                'isAnsweredCorrect': False
            })
    
    DB.registerPoll(callBack.from_user.id, quizDifficulty, sentPolls,sentPollsId)

    bot.send_message(callBack.message.chat.id, replyText, reply_markup=replyMarkup, parse_mode='html', disable_web_page_preview=True)
    logging.info(f"Start message: username: {callBack.from_user.first_name}, userId: {callBack.from_user.id}, message: {callBack.data}")


def handle_poll_answer(pollAnswer: PollAnswer, bot: TeleBot):
    logging.info('user answered')
    DB: Database = bot.db_connection

    DB.updatePollAnswer(pollAnswer.user.id, pollAnswer.poll_id, pollAnswer.option_ids)
    
    
def get_user_statistics(callBack: CallbackQuery, bot: TeleBot):
   
    DB: Database = bot.db_connection
    difficultyList=['junior', 'middle', 'senior']
    replyText=DB.standardMessages['statisticsIntro']
    
    for difficulty in difficultyList:
        numberOfTries=DB.getNumberOfTries(callBack.from_user.id, difficulty)
        numberOfPassed=DB.getNumberOfSuccessTries(callBack.from_user.id, difficulty)
        replyText=replyText+DB.standardMessages['statisticsLevel'].format(difficulty, numberOfTries, numberOfPassed)
    
    replyText=replyText[:-1]
    bot.send_message(callBack.message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    
