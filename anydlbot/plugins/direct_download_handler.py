# AnyDLBot - An Open Source ALL-In-One Telegram RoBot
# Copyright (C) 2018-2021 Shrimadhav U K & Authors

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import time
from datetime import datetime


from anydlbot import LOGGER
from anydlbot.config import Config
from anydlbot.helper_funcs.aiohttp_helper import direct_downloader
from anydlbot.helper_funcs.extract_link import get_link
from anydlbot.plugins.upload_handler import upload_worker
from strings import String


async def direct_dl_callback(bot, update):
    cb_data = update.data
    LOGGER.info(cb_data)
    # youtube_dl extractors
    send_as, _, __, ___ = cb_data.split("=")
    thumb_image_path = Config.WORK_DIR + "/" + str(update.from_user.id) + ".jpg"

    (
        url,
        custom_file_name,
        _,
        _,
    ) = get_link(update.message.reply_to_message)
    if not custom_file_name:
        custom_file_name = os.path.basename(url)

    description = String.CUSTOM_CAPTION_UL_FILE
    start_download = datetime.now()
    await bot.edit_message_text(
        text=String.DOWNLOAD_START,
        chat_id=update.message.chat.id,
        message_id=update.message.message_id,
    )
    tmp_directory_for_each_user = os.path.join(
        Config.WORK_DIR, str(update.from_user.id)
    )
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = os.path.join(tmp_directory_for_each_user, custom_file_name)

    c_time = time.time()
    try:
        await direct_downloader(
            url,
            download_directory,
            update.message,
            c_time,
        )
    except:
        return False

    if os.path.exists(download_directory):
        end_download = datetime.now()
        time_taken_for_download = (end_download - start_download).seconds
        await bot.edit_message_text(
            text=f"Download took {time_taken_for_download} seconds.\n"
            + String.UPLOAD_START,
            chat_id=update.message.chat.id,
            message_id=update.message.message_id,
        )
        try:
            upl = await upload_worker(
                update, custom_file_name, send_as, False, download_directory
            )
            LOGGER.info(upl)
        except:
            return False

        try:
            os.remove(download_directory)
            os.remove(thumb_image_path)
        except:
            pass
        await update.message.delete()

    else:
        await bot.edit_message_text(
            text=String.NO_VOID_FORMAT_FOUND.format("Incorrect Link"),
            chat_id=update.message.chat.id,
            message_id=update.message.message_id,
            disable_web_page_preview=True,
        )
