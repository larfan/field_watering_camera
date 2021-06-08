import tweepy,datetime,time, logging, picamera

#this init is also only needed temporarily for the reasons outlined above
camera = picamera.PiCamera()

#logging settings
LOG_FILENAME = '/home/pi/Documents/simplewateringsystem/field_watering_camera/logfile4.out'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
logging.info('This message should go to the log file / Start of run at: '+str(datetime.datetime.now()))


#credentials twitter API
consumer_key='FntFMPFx13PH4OvWVbqbFbqQ4'
consumer_secret_key='mLtwuKXgOtHBF2WHW5GbYN9kqFg4bzp0jkwBn2rUYhLIYDD23G'
access_token='1399406374107422721-kLr0L5tZBjoptCs5kRo0sDBAkRE3zj'
access_token_secret='z7RVF5DvadcWXskhjPIeeqYVO5xQQJJFWcaoQuTe65Rmp'

#authenticating to access the twitter API
auth=tweepy.OAuthHandler(consumer_key,consumer_secret_key)
auth.set_access_token(access_token,access_token_secret)
api=tweepy.API(auth)

#global variables
stateoftask=[False,False]   #takepicture,waterplants
lastuseoftask=[None,None]   #logs last use time
timeintervalltask=[10/3,10]     #how often task should be allowed to be called, in minutes
absolutetimes=[['17:45:00','18:00:00','18:20:00','19:10:00','19:50:00','20:30:00'],['17:50:00','18:400:00','19:40:00']]
cyclenr=0
lastmodificationtime=[datetime.datetime(1900,1,1),datetime.datetime(1900,1,1)]
exceptioncounter=0

def twitter(message, filename):
    global successfullupload
    successcounter=0
    while successcounter < 1:
        try:
            current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            imagetext=str(message)+' '+ current_time    
            if filename is not None:
                #Generate text tweet with media (image)
                imagelink='/home/pi/Documents/simplewateringsystem/field_watering_camera/pictures/%s.jpg' %filename
                
                api.update_with_media(imagelink,imagetext)
                print('Twitter function was used!')
            else: 
                api.update_status(imagetext)
                print('Twitter function was used!')

            
            
            successfullupload=True
            break
        
        except Exception as p:          #Exception as e instead of only exception, as to also gett traceback/error message
            
            successcounter+=1
            successfullupload=False
            time.sleep(1)
            print('Tweeting doesn\'t work nr: '+str(successcounter))
            
            #For debugging purposes: However tweepy.errors produce unnaturally long tracebacks, compared to other exceptions
            '''
            #get exception name & message
            print(type(p).__name__+': '+str(p))
            logging.exception('Got exception in twitter function')
            '''

def takepicture():
    current_time=datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    camera.start_preview()
    time.sleep(3)
    camera.capture('/home/pi/Documents/simplewateringsystem/field_watering_camera/pictures/'+current_time+".jpg")
    camera.stop_preview()
    
    print('Picture has been taken')
    #when it was used last time
    lastuseoftask[0]=datetime.datetime.now()
    #mark the task as done, relatively in the end(but before twitter function). so that function can be repeated if an error occured in the functional part
    stateoftask[0]=True                 #True in the sense that it has been used
    #post result on twitter
    twitter('State of the gARTen at ',current_time)

def waterplants(duration):
    # log when task was executed last time
    
    lastuseoftask[1]=datetime.datetime.now()    #this has to be placed before the time.sleep, otherwise adding up small delay

    print('Turn water on')
    time.sleep(duration)
    print('Turn water off')
    #post result on twitter
    watermessage='The vegetable field has been watered for '+ str(duration) + ' seconds ending at '
    #mark the task as done, relatively in the end(but before twitter function). so that function can be repeated if an error occured in the functional part
    stateoftask[1]=True                 #True in the sense that it has been used
    twitter(watermessage,None)
    
    


def resetprogress(usecase):            #usecase can either be, bytime or bytimeintervall. this function, shall check whether the funciton passed to it, has already been successfuly
    
    for index,element in enumerate(stateoftask):                                #executed in the specified time intervall. If it hasn't been, it lifts the block on it and  
        if element==False:
            pass               #this ensures that it doesn't run with bs values
        else:
            if usecase is 'bytimeintervall':
                currenttime=datetime.datetime.now()
                timedelta=currenttime-lastuseoftask[index]
                totalminutes=timedelta.total_seconds() / 60
                if totalminutes>=timeintervalltask[index]:
                    stateoftask[index]=False
                    
                print(timedelta.total_seconds() / 60)
            elif usecase is 'bytime':                   #this 'sub function' checks whether the current time is in a time window of 10 minutes, that is beginning with the times, that are found in the lists of absolutetimes
                #get current time as datetime object
                currenttimestring=datetime.datetime.now().strftime("%H:%M:%S") #pretty complicated, but you can't substract datetime.time() objects, therfore I convert a time string to a datetime.datetime object
                currenttime_asdatetime=datetime.datetime.strptime(currenttimestring,'%H:%M:%S')
                
                for ele in absolutetimes[index]:
                    #get difference between current time and tasktime in minutes
                    tasktime=datetime.datetime.strptime(ele,'%H:%M:%S') #this needs to be in the for loop as to get different 'eles', as in the different tasktimes if there are more than one
                    delta=currenttime_asdatetime-tasktime
                    deltaminutes=delta.total_seconds()/60
                    #calculate whether following if clause has been entered in the last 10 minutes
                    minutessincelastuse=(datetime.datetime.now()-lastuseoftask[index]).total_seconds() / 60
                    print(minutessincelastuse)
                    if 0<=deltaminutes<=10 and minutessincelastuse>10:
                        stateoftask[index]=False
                        
                    print(deltaminutes)
                    print('-----')
                    


while True:
    try:
        #header Output
        print('-----------------New Cycle '+str(cyclenr)+'-----------------')

        if stateoftask[0]==False:
            takepicture()
        if stateoftask[1]==False:
            waterplants(5)
        time.sleep(60)   #15
        print('This is statoftask before resetprogress()',stateoftask)
        resetprogress('bytimeintervall')
        #resetprogress('bytime')
        print('This is statoftask after resetprogress()',stateoftask)

        #formating ouput
        cyclenr+=1
    
    except:     #I don't know why, but logging doesn't seem to work when except Exception as e is used
        logging.exception('Got exception on main handler!!!!!!!!!!!!!'+str(datetime.datetime.now()))
        if exceptioncounter <3:
            exceptioncounter+=1
            print(exceptioncounter)
            print('THIS IS JUST a TEST')
            continue
        else:           #you should restart raspberry pi here
            logging.info('Amount of allowed exceptions exceeded! Attempted restart at: '+str(datetime.datetime.now()))
            break

        '''
        if type(p).__name__=='TweepError':      #trying to not log tweepy error
            print('just a twitter error')
            pass
        else:   
            logging.exception('Got exception on main handler______TEST')
            print('exception occured')
            break
            ''' 



if successfullupload==True:
    print('Uploading Image & Message was successfull.')
else:
    print('Uploading Image & Message wasn\'t successfull.')

print('Program finished')
