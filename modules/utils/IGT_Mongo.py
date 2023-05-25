#in this module connections to mondoDB is defined
import json


import pymongo
import jsonpickle
from telebot import types
import logging
import os
from datetime import datetime




class noMessagesToSend(Exception):
    def __str__(self):
        return 'fileTooBigError'


class noRecommendationsForThisQuestionaire(Exception):
    def __str__(self):
        return 'noRecommendationsForThisQuestionaire'

#Creating class for DB connection
class Database:
    
    standardMessages=[]
    

    def __init__(self, URL=os.environ.get('DB_STRING'), database='Database'):
        self.URL=URL
        self.databaseName=database
        

    def openConnection(self):
        self.client = pymongo.MongoClient(self.URL)
        database = self.client[self.databaseName]
        self.users= database['TG_Users']
        self.user_state= database['TG_User_State']
        self.standard_messages= database['TG_Standard_Messages']
        self.questions= database['TG_Questions']
        self.user_statistics=database['TG_User_Statistics']
        cursor = self.standard_messages.find()
        self.standardMessages = cursor[0]

        
    def closeConnection(self):
        self.client.close()

#check have this user used bot or not
    def isExistingUser(self, userId):
        
        filter_user = {'id': userId}
        if self.users.count_documents(filter_user)==0:   
            return False
        else:
            return True

    def getStandardMessages(self):
        cursor = self.standard_messages.find()
        return cursor[0]


    def getQuestions(self, difficulty):
        filter= {'difficulty': difficulty}

        cursor = self.questions.find(filter).sort("order", pymongo.ASCENDING)
        return cursor

    def increaseNumberOfTries(self, userId, difficulty):
        filter={'userid': userId}

        newnumber=self.getNumberOfTries(userId, difficulty)+1

        self.user_state.update_one(filter, { "$set":{'numberTries_'+difficulty: newnumber}})

    def registerPoll(self, userId, difficulty, polls, pollIds):
        userStatistics={
            'userid': userId,
            'difficulty': difficulty,
            'pollIds': pollIds,
            'isPassed': False,
            'questions': polls
        }
        self.user_statistics.insert_one(userStatistics)


    def updatePollAnswer(self, userId, pollId, selectedOption):
        filter={
            'userid': userId,
            'pollIds': {"$regex" : pollId}
            }
        Questinaire = self.user_statistics.find_one(filter)
        newQuestions=[]
        isAnswerCorrect=False
        
        for poll in Questinaire['questions']:
            
            if poll['id']==str(pollId):
                if poll['correctOptionId']==selectedOption[0]:
                    newQuestions.append({
                        'id': poll['id'],
                        'correctOptionId': poll['correctOptionId'],
                        'isAnsweredCorrect': True
                    })
                    isAnswerCorrect=True
                else:
                    newQuestions.append(poll)
            else:
                newQuestions.append(poll)
            

        countCorrect=0
        if isAnswerCorrect:
            self.user_statistics.update_one(filter,{ "$set":{'questions': newQuestions}})
            for question in newQuestions:
                if question['isAnsweredCorrect']:
                    countCorrect=countCorrect+1
            
            if countCorrect>2:
                self.user_statistics.update_one(filter,{ "$set":{'isPassed': True}}) 

            

#put User to default status
#We have tables TG_Users and TG_User_State - in default status it has False for search flag and -1 in account
    def setUserToDefault(self, user):
        
        filter_user = {'userid': user.id}
        user_json = json.loads(jsonpickle.encode(user))

        if self.isExistingUser(user.id):
            self.users.replace_one({'id': user.id}, user_json, upsert=True)
            #self.user_state.update_one(filter_user, { "$set":{'is_active_poll': False}})

            #self.poll_results.delete_many(filter_user)

            #self.poll_results.update_many(filter_user, {"$set": {'is_active_poll': False}})

        else:
            logging.info(f'Creating new user in DB userid: {user.id}')
            self.users.insert_one(user_json)
            
            defaultUserInfo = { 
                'userid': user.id,
                'name': user.first_name,
                'numberTries_junior': 0,
                'numberTries_middle': 0,
                'numberTries_senior': 0

            }
        

            self.user_state.insert_one(defaultUserInfo)
    
    def getNumberOfTries(self, userId, difficulty):
        filter={
            'userid': userId,
            'difficulty': difficulty
            }
        
        return self.user_statistics.count_documents(filter)



    def getNumberOfSuccessTries(self, userId, difficulty):
        filter={
            'userid': userId,
            'difficulty': difficulty,
            'isPassed': True
            }
        
        return self.user_statistics.count_documents(filter)
        

# # for testing
if __name__ == "__main__":



    DB =Database(URL = os.environ.get('DB_STRING_DEV'),database ='QB_Database')
    DB.openConnection()
    
   


    DB.closeConnection()