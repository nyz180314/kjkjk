from cheggscraper import Downloader
import sys
import boto3
import secrets
import logging
import os
from os import remove
import telegram
import asyncio
import time
import requests,json
from pyrogram import Client, filters
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
import siaskynet as skynet
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
import gspread
import random
from datetime import date, timedelta
from datetime import datetime
import logging

from telegram.constants import ParseMode
from telegram import __version__ as TG_VER
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = "6025537349:AAECCErbuGufl-6_8GE16YfBYuEpD6av_x8"
MainGroupID = -1001897727117
admins = ["5169338448","1019156002"]                                      
adminId = 1354393557
thread_id = None #289543
UserNameBot = "@cheggbhaiya11_bot"                       
UserNameChannel = "@cheggmxpro"                             
BD = 'MX'                                                   
BuySubscription = "https://t.me/"
BuySubscription2 = "https://t.me/"
PointPrices = "https://t.me/"
Channel = "https://t.me/"
Captcha = "https://bit.ly/"
GroupFree = "https://t.me/"                                           


global mi_update
global mi_context
mi_update = None
mi_context = None

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

#creds = ServiceAccountCredentials.from_json_keyfile_name("botchegg-d1b085aba480.json", scope)
# client = gspread.authorize(creds)
#sheet = client.open("BD_CheggBot2022").worksheet(f'{BD}')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")

async def echo(text,mi_context,mi_update,name, user_id, user_name):
    #cred = cred - 1
    #sheet.update_acell(f'K{fila}', f'{cred}')
    ahora = datetime.now()
    #despues = datetime.strptime(fechaCad, "%Y-%m-%d %H:%M:%S.%f")
    #delta = despues - ahora
    document1 = open('Answer.html', 'rb')
    user = mi_update.effective_user
    s3 = boto3.client('s3', region_name='us-east-1', 
                        aws_access_key_id='AKIAUGPUFCDFGEF3AT3H',
                        aws_secret_access_key='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',
                        config=boto3.session.Config(signature_version='s3v4'))
    bucket_name = 'nitin1312'
    file_name = 'Answer.html'
    GenToken = str(secrets.token_hex(16))
    s3.upload_file(file_name, bucket_name, f'{GenToken}.html', ExtraArgs={'ContentType': 'text/html'})
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket_name,
                'Key': f'{GenToken}.html'
                },
        ExpiresIn=3600 # 5 minutos
    )
    keyboard = [[InlineKeyboardButton("🌐 See Answer 🔓", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await mi_update.message.reply_text(f'𝐔𝐧𝐥𝐨𝐜𝐤𝐞𝐝 𝐋𝐢𝐧𝐤 🔐\n'
                                                         f'👁️‍🗨️ {user} 📥\n\n',
                                                       
                                        parse_mode=ParseMode.HTML,
                                        reply_markup=reply_markup,
                                        message_thread_id = thread_id)
    document1.close()
    remove("Answer.html")
    pass

async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global mi_update
    global mi_context
    mi_update = update
    mi_context = context
    chat_id=update.message.chat_id
    message_thread_id=update.message.message_thread_id
    #print(chat_id)
    print(message_thread_id)
    global id_mensaje
    id_mensaje = update.message.message_id
    #print(id_mensaje)
    #print(str(update.effective_user['id'])in admins)
    if message_thread_id != 1 or message_thread_id == thread_id:
        print("Estas en el Canal Correcto")
        text = update.message.text
        textDiv = text.split(sep=' ')
        comando = textDiv[0]
        print(comando)
        #if comando == '/get' or comando == f'/get{UserNameBot}' or comando == '/mydata' or comando == f'/mydata{UserNameBot}':
           # user_id = str(update.effective_user['id'])
            #encontrarIdUsuario = sheet.find(user_id)
            #if not encontrarIdUsuario:
               # puntos = 1000  # Here you can put the points you want to give for the first time they register.
                #cont = sheet.acell('J1').value
                #contador = int(cont)
                #id = contador
              #  nombre = update.effective_user['first_name']
              #  apellido = update.effective_user['last_name']
               # usuario = update.effective_user['username']
                #fecha_ini = datetime.now()
                #fecha_fin = fecha_ini + timedelta(days=5)
                #contador = contador + 1
                #sheet.update_acell(f'F{contador}', f'{fecha_ini}')
                #sheet.update_acell(f'G{contador}', f'{fecha_fin}')
                #sheet.update_acell(f'A{contador}', f'{id}')
                #sheet.update_acell(f'B{contador}', f'{user_id}')
                #sheet.update_acell(f'C{contador}', f'{usuario}')
                #sheet.update_acell(f'D{contador}', f'{nombre}')
                #sheet.update_acell(f'E{contador}', f'{apellido}')
                #sheet.update_acell(f'K{contador}', f'{puntos}')
                #encontrarIdUsuario = sheet.find(user_id)
                #encontrarPuntosUsuario = int(sheet.acell(f'K{encontrarIdUsuario.row}').value)
                #encontrarFecha_finUsuario = sheet.acell(f'G{encontrarIdUsuario.row}').value
                #fechaFinal = datetime.strptime(encontrarFecha_finUsuario, "%Y-%m-%d %H:%M:%S.%f")
                #diferencia = fechaFinal - datetime.now()
                #sheet.update_acell(f'J1', f'{contador}')
            #await update.message.reply_text(f"Remaining  chances: \n\n"
                                        #f"Your points expire after: \n"
                                        #f"{diferencia.days} Day/s⏱⏳\n"
                                        #f"---------\n"
                                        #f"{datetime.now()}  UTC+05:30")
            #else:
                #encontrarPuntosUsuario = int(sheet.acell(f'K{encontrarIdUsuario.row}').value)
                #encontrarFecha_finUsuario = sheet.acell(f'G{encontrarIdUsuario.row}').value
                #fechaFinal = datetime.strptime(encontrarFecha_finUsuario, "%Y-%m-%d %H:%M:%S.%f")
                #diferencia = fechaFinal - datetime.now()
                #if int(diferencia.days) <= 0:
                    #sheet.update_acell(f'G{encontrarIdUsuario.row}', f'{datetime.now()}')
               # await update.message.reply_text(f"Remaining  chances: {encontrarPuntosUsuario}\n\n"
                                        #f"Your points expire after: \n"
                                        #f"{diferencia.days} Day/s⏱⏳\n"
                                        #f"---------\n"
                                       # f"{datetime.now()}  UTC+05:30")
        
        #if comando == '/add' and str(update.effective_user['id']) in admins:
         #   print("Estas en el Comando ADD")
          #  points = textDiv[1]
           # days = textDiv[2]
            #UserIdR = str(update.effective_message.reply_to_message.from_user.id)
            #encontrarIdUsuario = sheet.find(UserIdR)
            #encontrarPuntosUsuario = int(sheet.acell(f'K{encontrarIdUsuario.row}').value)
            #encontrarFecha_finUsuario = sheet.acell(f'G{encontrarIdUsuario.row}').value
            #fechaFinal = datetime.strptime(encontrarFecha_finUsuario, "%Y-%m-%d %H:%M:%S.%f")
            #f = fechaFinal + timedelta(days=int(days))
            #sheet.update_acell(f'K{encontrarIdUsuario.row}', f'{encontrarPuntosUsuario + int(points)}')
            #sheet.update_acell(f'G{encontrarIdUsuario.row}', f'{f}')
            #encontrarPuntosUsuario = int(sheet.acell(f'K{encontrarIdUsuario.row}').value)
            #encontrarFecha_finUsuario = sheet.acell(f'G{encontrarIdUsuario.row}').value
            #fechaFinal = datetime.strptime(encontrarFecha_finUsuario, "%Y-%m-%d %H:%M:%S.%f")
            #diferencia = fechaFinal - datetime.now()
            #await update.message.reply_text(f"Remaining  chances: {encontrarPuntosUsuario}\n\n"
            #                        f"Your points expire after: \n"
             #                       f"{diferencia.days} Day/s ⏱⏳\n"
              #                      f"---------\n"
               #                     f"{datetime.now()}  UTC+05:30")
           # await mi_context.bot.sendMessage(chat_id = adminId,
            #                                 text= f"User ID: {UserIdR}\n"
             #                                      f"{days} Days.\n"
              #                                     f"{points} Points.\n\n"
               #                                    f"Added by: {str(update.effective_user['id'])}"
                #                            )
   
            
        if os.path.exists('Answer.html'):
            print("If there is an HTML file")
            remove("Answer.html")
            await chegg(update, context)
        else:
            print("No HTML File")
            await chegg(update, context)
    else:
        pass

async def chegg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    boton5 = InlineKeyboardButton(text='🥚Chegg Unlocks [FREE]🆓', url=f'{GroupFree}')
    boton3 = InlineKeyboardButton(text='🥷💰 Buy a Subscription 💵', url=f'{BuySubscription}')
    boton4 = InlineKeyboardButton(text='🇮🇳💰 Buy a Subscription 💵', url=f'{BuySubscription2}')
    boton1 = InlineKeyboardButton(text='💰 Point Prices 💵', url=f'{PointPrices}')
    boton2 = InlineKeyboardButton(text='🎓 Join the Channel', url=f'{Channel}')
    global UUID
    UUID = None
    global name, user_id, user_name, Bandera, cred, fila, fechaCad
    name = update.effective_user['first_name']
    user_id = str(update.effective_user['id'])
    user_name = update.effective_user['username']
    Bandera = 0
    text = update.message.text
    encontrarIdUsuario = None
    #encontrarIdUsuario = sheet.find(user_id)
    
        #print("Si esta en la base de datos")
   # coordenadas = [int(encontrarIdUsuario.col), int(encontrarIdUsuario.row)]
   # fila = int(encontrarIdUsuario.row)
    

    if text.startswith("https://www.chegg.com/homework-help/questions-and-answers/") or text.startswith("https://www.chegg.com/homework-help/"):
        #if coordenadas[0] > 0 and coordenadas[1] > 0:
            #fecha = datetime.now()
            #fechaCad = sheet.acell(f'G{fila}').value
            #cred = int(sheet.acell(f'K{fila}').value)
            #fecha_dt = datetime.strptime(fechaCad, "%Y-%m-%d %H:%M:%S.%f")
            #print(f"El Usuario tiene: {cred} Puntos.")
            #if fecha < fecha_dt:
                #if cred > 0:
                    await Downloader.main(text,mi_context,mi_update,name, user_id, user_name,  )
                    pass
                #else:
                    
    else:
                pass
        
        
def main() -> None:
    
    application = Application.builder().token(f"{TOKEN}").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler (MessageHandler(filters.Chat(int(MainGroupID)) & filters.TEXT, comandos))
    
    application.run_polling()
    

if __name__ == "__main__":
     main()

