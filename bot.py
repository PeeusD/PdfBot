﻿from fileinput import filename
from telegram import ChatAction, Bot, ParseMode
from os import getenv, rename, remove, path, walk
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
import PyPDF2 as pd
import re
from time import sleep
import requests
from functools import wraps
from datetime import datetime
load_dotenv()

# TARGET_CHAT_ID = getenv('CHAT_ID')
MY_CHAT_ID = getenv('CHAT_ID2')
TOKEN = getenv('TOKEN')
USER1 = int(getenv('USER1'))
USER2 = int(getenv('USER2'))
USER3 = int(getenv('USER3'))

bot = Bot(token=TOKEN)


LIST_OF_ADMINS = [USER1, USER2, USER3]

def restricted(func):
    @wraps(func)
    def wrapped(update, context):
        user_id = update.effective_user.id
      
        if user_id not in LIST_OF_ADMINS:
            print(f"Person with userId: {user_id} has Unauthorized accessed bot!")
            return
        return func(update, context)
    return wrapped


@restricted
def start(update, context):
       update.message.reply_text(f'Send Me ur PDF :')

@restricted
def greetings(update, context=bot):
        #printing date 
        dat = datetime.today().strftime('%d %B %Y')
            #daily quotes api
        url = "https://api.quotable.io/random"

        response =  requests.get(url)
        json_data = response.json()
        #sending message to channel...
        msg = f"🌞 *Good Morning! *🌞  \n_{dat} \n{json_data['content']} \n- {json_data['author']}_"
        bot.send_message(chat_id=update.effective_message.chat_id, text=msg, parse_mode= ParseMode.MARKDOWN)

@restricted
def forward_mgmt (update, context) :
        msg_id = update.message.message_id
        context.bot.copy_message(chat_id=MY_CHAT_ID, from_chat_id=update.effective_message.chat_id, message_id=msg_id)
        

@restricted
def pdf_mgmt (update, context) :
        
        message = update.message.reply_text("--Processing...and...Searching--")
        
        file_id = update.message.document.file_id  #getting file id
        fileName = update.message.document.file_name   #getting filename
        newFile = bot.get_file(file_id)
  
        if fileName.startswith('UPSC'):
            newFile.download()


            pattern = 'DAILY NEWSPAPERS PDF'
        
            dir_path = path.dirname(path.abspath(__file__))
            
            #renaming pdfs
            for root, dirs, files in walk(dir_path):
                for file in files: 
                    
                    if file.startswith('file'):
                        
                        rename(file, fileName)
                    
                        merger = pd.PdfFileMerger( strict=True)
                        merger.append(pd.PdfFileReader(path.join(root,'promo.pdf')))
                        merger.append(pd.PdfFileReader(path.join(root,fileName)))
                        
                        merger.write(fileName)
                        merger.close()
                    


            #getting no. of pages for pdfs
                        infile = pd.PdfFileReader(path.join(root,fileName))
                        numPages = infile.getNumPages()
                        
                        
                        delPages = []

                        for i in range(0, numPages):
                            pageObj = infile.getPage(i)
                            ex_text = pageObj.extractText()

                            
                            if re.search(pattern, ex_text):
                                
                                # print(f'Pattern found on Page no: {i}')
                                delPages.append(i)


                        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
                        #searching required text in pdfs...
                        message_id = message.message_id
                        sleep(3)
                        bot.delete_message(chat_id=update.effective_message.chat_id, message_id= message_id)
                        update.message.reply_text(f'Pattern found in Page nos.: {delPages}')
                        
                        
                        #deleting required pages and uploading to telegram...
                        if len(delPages) > 0 :
                            infile = pd.PdfFileReader(path.join(root,fileName))
                            output = pd.PdfFileWriter()
                            
                            for i in range(infile.getNumPages()):
                                if i not in delPages:
                                    p = infile.getPage(i)
                                    output.addPage(p)

                            with open(path.join(root,fileName),'wb') as f:
                                output.write(f)
                            
                        
                            update.message.reply_text(f'{delPages} Pages have been deleted!')
                            #uploading...
                            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.UPLOAD_DOCUMENT)
                            #Sending files to user...
                            context.bot.send_document(chat_id=update.effective_message.chat_id, thumb=open('thumb.jpg', 'rb'), document=open(fileName, 'rb'), timeout=240)
                            #uploading docs to channel
                            # context.bot.send_document(chat_id=CHAT_ID2, thumb=open('thumb.jpg', 'rb'), document=open(fileName, 'rb'), timeout=240)

                        else:
                            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
                            update.message.reply_text(f"Word: '{pattern}' not found in PDF!")
                            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.UPLOAD_DOCUMENT)
                            #For sending files to User
                            context.bot.send_document(chat_id=update.effective_message.chat_id, thumb=open('thumb.jpg', 'rb'), document=open(fileName, 'rb'), timeout=240)
                            #sending files to channel
                            # context.bot.send_document(chat_id=CHAT_ID2, thumb=open('thumb.jpg', 'rb'), document=open(fileName, 'rb'), timeout=240)
                        
                        remove(path.join(root,fileName))  #delting pdf from directory

                   

                        # print('File deleted!')
                    
updater = Updater(TOKEN)
# updater.dispatcher.add_handler(CommandHandler('start', start))
# updater.dispatcher.add_handler(CommandHandler('greet', greetings))

updater.dispatcher.add_handler(MessageHandler(Filters.chat_type.private, forward_mgmt))
# updater.dispatcher.add_handler(MessageHandler(Filters.chat_type.private, pdf_mgmt))
updater.start_polling()
updater.idle()
