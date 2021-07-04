from telegram import ChatAction, Bot
from os import getenv, rename, remove, path, walk
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
import PyPDF2 as pd
import re

load_dotenv()

TOKEN = getenv('TOKEN')
bot = Bot(token=TOKEN)

def start(update, context):
       
    update.message.reply_text(f'Send Me ur PDF :  ')

def pdf_mgmt (update, context) :
        
    try:   
        update.message.reply_text("***Processing***")
        file_id = update.message.document.file_id  #getting file id
        fileName = update.message.document.file_name   #getting filename
        newFile = bot.get_file(file_id)
        newFile.download()
        
        pattern = 'DAILY NEWSPAPERS PDF'
       
        dir_path = path.dirname(path.realpath(__file__))
  
        for root, dirs, files in walk(dir_path):
            for file in files: 
        
                if file.endswith('.pdf'): 
                    rename(file, fileName)
        

        infile = pd.PdfFileReader(fileName, 'rb')
        numPages = infile.getNumPages()
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        update.message.reply_text("Searching...")
        delPages = []

        for i in range(0, numPages):
            pageObj = infile.getPage(i)
            ex_text = pageObj.extractText()
            
            if re.search(pattern, ex_text):
                
                # print(f'Pattern found on Page no: {i}')
                delPages.append(i)

        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        update.message.reply_text(f'Pattern found in Page nos.: {delPages}')

        if len(delPages) > 0 :
            infile = pd.PdfFileReader(fileName, 'rb')
            output = pd.PdfFileWriter()

            for i in range(infile.getNumPages()):
                if i not in delPages:
                    p = infile.getPage(i)
                    output.addPage(p)

            with open(fileName, 'wb') as f:
                output.write(f)
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
            update.message.reply_text(f'{delPages} Pages have been deleted!')
            #uploading...
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.UPLOAD_DOCUMENT)
            context.bot.send_document(chat_id=update.effective_message.chat_id, document=open(fileName, 'rb'), timeout=240)

        else:
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
            update.message.reply_text(f"Word: '{pattern}' not found in PDF!")
        remove(fileName)    
    except Exception as e:
        print(e)
          
    

updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.chat_type.private, pdf_mgmt))
updater.start_polling()
updater.idle()