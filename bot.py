from telegram import ChatAction, Bot, ParseMode
from os import getenv, rename, remove, path, walk
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
import PyPDF2 as pd
import re
from time import sleep
import requests
from datetime import datetime
load_dotenv()

CHANNEL_ID = getenv('CHANNEL_ID')
TOKEN = getenv('TOKEN')

bot = Bot(token=TOKEN)

def start(update, context):
       
    update.message.reply_text(f'Send Me ur PDF :')


def greetings(update, context=bot):
        
        dat = datetime.today().strftime('%d %B %Y')


        url = "https://api.quotable.io/random"

        response =  requests.get(url)
        json_data = response.json()
      
        msg = f"🌞 *Good Morning!*  \n📅_{dat} \n📝{json_data['content']} \n- {json_data['author']}_"
        bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode= ParseMode.MARKDOWN)





def pdf_mgmt (update, context) :
        
    try:   
        
        message = update.message.reply_text("***Processing...and...Searching***")
        
        file_id = update.message.document.file_id  #getting file id
        
        fileName = update.message.document.file_name   #getting filename
        newFile = bot.get_file(file_id)
        newFile.download()

        

        pattern = 'DAILY NEWSPAPERS PDF'
       
        dir_path = path.dirname(path.abspath(__file__))
        
        #renaming pdfs
        for root, dirs, files in walk(dir_path):
            for file in files: 
                
                if file.startswith('file'):
                    
                    rename(file, fileName)
                   
                    merger = pd.PdfFileMerger()
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
                        #For debugging use update eff....
                        context.bot.send_document(chat_id=CHANNEL_ID, document=open(fileName, 'rb'), timeout=240)

                    else:
                        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
                        update.message.reply_text(f"Word: '{pattern}' not found in PDF!")
                        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.UPLOAD_DOCUMENT)
                        #For debugging use update eff...
                        context.bot.send_document(chat_id=CHANNEL_ID, document=open(fileName, 'rb'), timeout=240)
                    
                    remove(path.join(root,fileName))  #delting pdf from directory
                    print('File deleted!')
                    
    except Exception as e:
       print(e)

updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('greet', greetings))

updater.dispatcher.add_handler(MessageHandler(Filters.chat_type.private, pdf_mgmt))
updater.start_polling()
updater.idle()