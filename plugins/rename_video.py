#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Ns_AnoNymouS 

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import time
import random
# the secret configuration specific things
from sample_config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import Client, Filters
from helper_funcs.help_Nekmo_ffmpeg import take_screen_shot
from helper_funcs.display_progress import progress_for_pyrogram

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image

from pyrogram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton	
from pyrogram.errors import UserNotParticipant, UserBannedInChannel	
from database.database import *	


@pyrogram.Client.on_message(pyrogram.Filters.command(["rename_as_video"]))
async def rename_video(bot, update):
    try:	
        await bot.get_chat_member(	
        chat_id=Config.AUTH_CHANNEL,	
        user_id=update.from_user.id	
        )	
    except pyrogram.errors.exceptions.bad_request_400.UserNotParticipant:	
        await bot.send_message(	
            chat_id=update.chat.id,	
            text=Translation.AUTH_CHANNEL_TEXT,	
            parse_mode="html",	
            reply_to_message_id=update.message_id,	
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text = '✔️ Updates Channel', url = "https://t.me/myTestbotz")]])	
        )	
        return
    if update.from_user.id in Config.BANNED_USERS:
        await update.reply_text("""<b>you are B A N N E D</b>
For MisUsing This Free Service""")
        return
    if (" " in update.text) and (update.reply_to_message is not None):
        cmd, file_name = update.text.split(" ", 1)
        if len(file_name) > 75:
            await update.reply_text(
                Translation.IFLONG_FILE_NAME.format(
                    alimit="75",
                    num=len(file_name)
                )
            )
            return
        description = Translation.CUSTOM_CAPTION_UL_FILE
        download_location = Config.DOWNLOAD_LOCATION + "/"
        b = await bot.send_message(
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
                b,
                c_time
            )
        )
        if the_real_download_location is not None:
            try:
                await bot.edit_message_text(
                    text=Translation.SAVED_RECVD_DOC_FILE,
                    chat_id=update.chat.id,
                    message_id=b.message_id
                )
            except:
                pass
            new_file_name = download_location + file_name
            os.rename(the_real_download_location, new_file_name)
            await bot.edit_message_text(
                text=Translation.UPLOAD_START,
                chat_id=update.chat.id,
                message_id=b.message_id
                )
            logger.info(the_real_download_location)
            width = 0
            height = 0
            duration = 0
            metadata = extractMetadata(createParser(new_file_name))
            try:
             if metadata.has("duration"):
                duration = metadata.get('duration').seconds
            except:
              pass
            thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
            if not os.path.exists(thumb_image_path):
               try:
                    thumb_image_path = await take_screen_shot(new_file_name, os.path.dirname(new_file_name), random.randint(0, duration - 1))
               except:
                    thumb_image_path = None
            else:
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                # img.thumbnail((90, 90))
                img.resize((320, height))
                img.save(thumb_image_path, "JPEG")
                # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
            c_time = time.time()
            await bot.send_video(
                chat_id=update.chat.id,
                video=new_file_name,
                duration=duration,
                thumb=thumb_image_path,
               # caption=description,
                caption=f"""<b>{file_name}
                
Renamed by @TgRenamebot</b> """,
                # reply_markup=reply_markup,
                reply_to_message_id=update.reply_to_message.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    b, 
                    c_time
                )
            )
            try:
                os.remove(new_file_name)
                #os.remove(thumb_image_path)
            except:
                pass
            await bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.chat.id,
                message_id=b.message_id,
                disable_web_page_preview=True
            )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.REPLY_TO_VIDEO_FOR_RENAME_FILE,
            parse_mode="html",
            disable_web_page_preview=True,
            reply_to_message_id=update.message_id
        )
