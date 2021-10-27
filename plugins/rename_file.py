#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import time

# the secret configuration specific things
from sample_config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import Client, filters

from helper_funcs.display_progress import progress_for_pyrogram
from helper_funcs.timegap_check import timegap_check

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image

from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, UserBannedInChannel
from database.database import *

@pyrogram.Client.on_message(pyrogram.filters.command(["rename"]))
async def rename_doc(bot, update):
    
    update_channel = Config.UPDATE_CHANNEL
    if update_channel:
        try:
            user = await bot.get_chat_member(update_channel, update.chat.id)
            if user.status == "kicked":
               await update.reply_text(Translation.ACCESS_DENIED)
               return
        except UserNotParticipant:
            await update.reply_text(text=Translation.JOIN_NOW_TEXT,
                  reply_markup=InlineKeyboardMarkup( [ [ InlineKeyboardButton(text="ᴊᴏɪɴ ɴᴏᴡ 🔓", url=f"https://t.me/{Config.UPDATE_CHANNEL}") ]
                ] 
              )
            )
            return
        except Exception:
            await update.reply_text(Translation.CONTACT_MY_DEVELOPER)
            return
       ########################## TIME GAP #####################  
    if update.from_user.id not in Config.AUTH_USERS:
      if Config.TIME_GAP:
        time_gap = await timegap_check(update)
        if time_gap:
            return
        Config.TIME_GAP_STORE[update.from_user.id] = time.time()
        asyncio.get_event_loop().create_task(notify(update, Config.TIME_GAP))
  ############################################# 
    if update.from_user.id in Config.BANNED_USERS:
        await update.reply_text("""<b> You are B A N N E D </b>
        For MisUsing This Free Service""")
        return

    if (" " in update.text) and (update.reply_to_message is not None):
        
        cmd, file_name = update.text.split(" ", 1)
        if len(file_name) > 130:
            await update.reply_text(
                Translation.IFLONG_FILE_NAME.format(
                    alimit="130",
                    num=len(file_name)
                )
            )
            return
        description = Translation.CUSTOM_CAPTION_UL_FILE
        download_location = Config.DOWNLOAD_LOCATION + "/"
        a = await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.DOWNLOADING,
            reply_to_message_id=update.message_id
        )
        c_time = time.time()
        the_real_download_location = await bot.download_media(
            message=update.reply_to_message,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(
                Translation.DOWNLOAD_START,
                a,
                c_time
            )
        )
        if the_real_download_location is not None:
            try:
                await bot.edit_message_text(
                    text=Translation.SAVED_RECVD_DOC_FILE,
                    chat_id=update.chat.id,
                    message_id=a.message_id
                )
            except:
                pass
            new_file_name = download_location + file_name
            os.rename(the_real_download_location, new_file_name)
            logger.info(the_real_download_location)
            thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
            if not os.path.exists(thumb_image_path):
                mes = await thumb(update.from_user.id)
                if mes != None:
                    m = await bot.get_messages(update.chat.id, mes.msg_id)
                    await m.download(file_name=thumb_image_path)
                    thumb_image_path = thumb_image_path
                else:
                    thumb_image_path = None

            c_time = time.time()
            await bot.send_document(
                chat_id=update.chat.id,
                document=new_file_name,
                thumb=thumb_image_path,
               # caption=description,
                caption=f"""<b>{file_name}  </b>    
                
""",

                # reply_markup=reply_markup,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('⭕Share & Support⭕', url='http://t.me/share/url?url=Hey%20There%E2%9D%A4%EF%B8%8F%2C%0A%20%20%0A%20%20I%20Found%20A%20Really%20Awesome%20Bot%20%20For%20Rename%20any%20Telegram%20Medias%20%26%20File%20With%20Permanent%20Thumbnail%20Support%0A%20%20Hope%20This%20Bot%20Helps%20You%20Too.%E2%9D%A4%EF%B8%8F%E2%9D%A4%EF%B8%8F%E2%9D%A4%EF%B8%8F%0A%20%20%0A%20%20Bot%20Link%20%3A-%20%40TGRenameBot')]]),
                reply_to_message_id=update.reply_to_message.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    a, 
                    c_time
                )
            )
            try:
                os.remove(new_file_name)
                os.remove(thumb_image_path)
            except:
                pass
            await a.delete ()
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.REPLY_TO_DOC_FOR_RENAME_FILE,
            parse_mode="html",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📝How to RenameFile', url='http://t.me/mytestbotz/26')]]),
            reply_to_message_id=update.message_id
        )

################################
async def notify(update, time_gap):
    await asyncio.sleep(30)
    await update.reply_text("Please wait 30 more second before Next Request")
    await asyncio.sleep(time_gap)
    await update.reply_text("__You can use me Now 😌__")     
