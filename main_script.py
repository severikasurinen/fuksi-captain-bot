from __future__ import unicode_literals
from queue import PriorityQueue
import os
import csv
import re
import time
import datetime
import html
import json
import traceback
import subprocess
import random
import Levenshtein
import requests
import schedule
from threading import Thread
from bs4 import BeautifulSoup
# Remember to run install commands before importing new packages!

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import *

import config
import message_handling
import strings

forwarding_timeout = 60  # Time in seconds that forwarding stays active for
pseudonym_timeout = 72  # Time in hours to keep pseudonym for
spam_cooldown = 10  # Time in minutes to wait between sending stickers, etc.
max_instant_requests = 20  # Max. broadcast messages instantly (API limit ~30 users per second)
max_instant_requests_personal = 1  # Max. broadcast messages instantly to single chat (API limit 1 per second)
request_cooldown = 1  # Broadcast cooldown in seconds

application = Application.builder().token(config.BOT_TOKEN).build()
start_time = 0
request_queue = PriorityQueue()
queue_id = 0
broadcasts_sent = 0
previous_broadcast = []
command_count = {'start': 0, 'help': 0, 'info': 0, 'song': 0, 'fact': 0, 'previous': 0, 'exit': 0}


def get_chat_ids():
    """Get a list of chat IDs."""
    chat_ids = []
    with open(config.DATABASE_FILE, newline='') as fp:
        for line in fp.readlines():
            chat_ids.append((int(line)))

    return chat_ids


def get_queue_id():
    global queue_id
    queue_id += 1
    return queue_id


def next_file_name():
    name_counter = 0
    date_string = datetime.datetime.now().strftime('%y-%m-%d')
    if not os.path.exists(config.BROADCAST_FILES_DIR):
        os.makedirs(config.BROADCAST_FILES_DIR)
    for fn in os.listdir(config.BROADCAST_FILES_DIR):
        if fn.split('_')[0] == date_string:
            name_counter += 1
    return date_string + '_' + str(name_counter)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    message_handling.user_songs[int(query.data.split(':')[0])] = query.data.split(':')[1]  # Temp. save selected song
    await query.edit_message_text(text=f"'{query.data.split(':')[1]}'" + strings.SONG_SELECTED[config.LANGUAGE])


def save_broadcasts(broadcasts, new_msg=None, new_file=None, edit=False):
    """Save broadcast to database."""
    with open(config.BROADCASTS_FILE, 'w') as f:
        if not edit:
            for broadcast in broadcasts:
                f.write('<-@\n' + broadcast + '\n@->\n')
        else:
            for broadcast in broadcasts[:-1]:
                f.write('<-@\n' + broadcast + '\n@->\n')

        if new_file:
            file_tag = '<@|' + new_file + '|@>\n'
        else:
            file_tag = ''

        if new_msg:
            if not edit:
                f.write('<-@\n' + file_tag + datetime.datetime.now().strftime('<b>%d.%m.%Y</b>\n---\n') + new_msg
                        + '\n@->\n')
            else:
                prev_tag = '\n'.join(broadcasts[-1].split('\n')[:broadcasts[-1].split('\n').index('---') + 1]) + '\n'
                f.write('<-@\n' + prev_tag + new_msg + '\n@->\n')


def get_broadcasts():
    """Get a list of previous broadcasts."""
    prev_broadcasts = []
    temp_broadcast = ""
    with open(config.BROADCASTS_FILE, 'r') as f:
        for line in f:
            if line == '<-@\n':
                temp_broadcast = ""
            elif line == '@->\n':
                prev_broadcasts.append(temp_broadcast)
            else:
                temp_broadcast += line
    return prev_broadcasts


def add_temp_user(user_id, spam=False):
    """Add user to temporary pseudonym list."""
    temp_users = get_temp_users()
    if user_id not in temp_users.keys():
        temp_users[user_id] = ['', '', '']

        id_num = 0
        unique_name = True
        while True:
            new_pseudonym = (random.choice(strings.PSEUDONYMS) + ' '
                             + datetime.datetime.now().strftime('%d') + '-' + str(id_num))
            for key in temp_users.keys():
                if temp_users[key][1] == new_pseudonym:
                    id_num += 1
                    unique_name = False
                    break
            if unique_name:
                break
            else:
                unique_name = True
        temp_users[user_id][1] = new_pseudonym

    temp_users[user_id][0] = datetime.datetime.now()

    if spam:
        temp_users[user_id][2] = 'S'
    else:
        temp_users[user_id][2] = '-'

    with open('temp_users.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        for key in temp_users.keys():
            writer.writerow([key, temp_users[key][0].strftime('%d-%m-%y %H:%M:%S'), temp_users[key][1],
                             temp_users[key][2]])

    return temp_users[user_id][1]  # Return pseudonym


def get_temp_users():
    """Get list of temporary pseudonyms"""
    temp_users = {}
    if not os.path.exists('temp_users.csv'):
        f = open('temp_users.csv', 'w')
        f.close()

    with open('temp_users.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for line in csvreader:
            if len(line) > 3:
                temp_users[int(line[0])] = [datetime.datetime.strptime(line[1], '%d-%m-%y %H:%M:%S'), line[2], line[3]]
                if (datetime.datetime.now() - temp_users[int(line[0])][
                    0]).total_seconds() / 60 / 60 > pseudonym_timeout:
                    temp_users.pop(int(line[0]))

    if len(temp_users.keys()) == 0:
        message_handling.clear_messages()
    return temp_users


def is_admin(user_id):
    """Check if user is an admin."""
    return user_id in config.BOT_ADMINS


def is_moderator(user_id):
    """Check if user is an admin."""
    return is_admin(user_id) or user_id in config.BOT_MODERATORS


def is_user(user_id):
    """Check if user exists."""
    return user_id in get_chat_ids()


def clean_input(input_text):
    """Remove special characters from string."""
    result = re.sub('[\W_]+', '', input_text)
    return result.lower()


async def start_command(update, context):
    """Command for creating a user."""
    command_count['start'] = command_count['start'] + 1

    chat_ids = get_chat_ids()
    if update.message.chat.id not in chat_ids:
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.START_MSG[config.LANGUAGE], parse_mode='HTML')))
        print("New user! :)")
        chat_ids.append(update.message.chat.id)

        with open(config.DATABASE_FILE, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            for chat_id in chat_ids:
                writer.writerow([str(chat_id)])
    else:
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.ALREADY_USER[config.LANGUAGE], parse_mode='HTML')))


async def exit_command(update, context):
    """Command for removing a user."""
    command_count['exit'] = command_count['exit'] + 1

    if not is_user(update.message.chat.id):
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_USER[config.LANGUAGE], parse_mode='HTML')))
        return

    print("Lost a user! :(")

    chat_ids = get_chat_ids()
    with open(config.DATABASE_FILE, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        for chat_id in chat_ids:
            if chat_id != update.message.chat.id:
                writer.writerow([str(chat_id)])
    request_queue.put((4, get_queue_id(), update.message.chat.id,
                       lambda: update.message.reply_text(strings.USER_DELETED[config.LANGUAGE], parse_mode='HTML')))


async def help_command(update, context):
    """Command for getting instructions."""
    command_count['help'] = command_count['help'] + 1

    if not is_user(update.message.chat.id):
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_USER[config.LANGUAGE], parse_mode='HTML')))
        return

    help_msg = strings.HELP_MSG[config.LANGUAGE]
    if is_moderator(update.message.chat.id):
        help_msg += strings.HELP_MSG_ADMIN
    request_queue.put((4, get_queue_id(), update.message.chat.id,
                       lambda: update.message.reply_text(help_msg, parse_mode='HTML')))


async def info_command(update, context):
    """Command for getting important information."""
    command_count['info'] = command_count['info'] + 1

    if not is_user(update.message.chat.id):
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_USER[config.LANGUAGE], parse_mode='HTML')))
        return
    request_queue.put((4, get_queue_id(), update.message.chat.id,
                       lambda: update.message.reply_text(strings.INFO_MSG[config.LANGUAGE], parse_mode='HTML',
                                                         disable_web_page_preview=True)))


async def fact_command(update, context):
    """Command to receive the teekkari fact of the week."""
    command_count['fact'] = command_count['fact'] + 1

    if not is_user(update.message.chat.id):
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_USER[config.LANGUAGE], parse_mode='HTML')))
        return

    cur_week = datetime.date.today().isocalendar()[1]  # Current calendar week
    with open(config.FACTS_FILE, encoding="utf8") as fp:
        lines = fp.readlines()
        i = 0
        for line in lines:
            if cur_week == i + 1:
                if len(line) > 0:
                    request_queue.put((4, get_queue_id(), update.message.chat.id,
                                       lambda: update.message.reply_text(strings.FACT_PREFIX[config.LANGUAGE]
                                                                         + str(cur_week)
                                                                         + strings.FACT_SUFFIX[config.LANGUAGE] + line,
                                                                         parse_mode='HTML')))
                    return
                else:
                    request_queue.put((4, get_queue_id(), update.message.chat.id,
                                       lambda: update.message.reply_text(strings.FACT_NOT_FOUND[config.LANGUAGE],
                                                                         parse_mode='HTML')))
                    return
            i += 1
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.FACT_NOT_FOUND[config.LANGUAGE],
                                                             parse_mode='HTML')))


async def song_command(update, context):
    """Command for teekkari song memory game."""
    command_count['song'] = command_count['song'] + 1

    if not is_user(update.message.chat.id):
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_USER[config.LANGUAGE], parse_mode='HTML')))
        return

    if update.message.text:
        inline_keyboard = [[]]
        i = 0
        for key in strings.LYRICS:
            cur_button = InlineKeyboardButton(key, callback_data=str(update.message.chat.id) + ':' + key)
            if i % 2 == 0:
                inline_keyboard.append([cur_button])
            else:
                inline_keyboard[-1].append(cur_button)
            i += 1

        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.WHICH_SONG[config.LANGUAGE],
                                                             reply_markup=reply_markup)))
    else:
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.INVALID_COMMAND[config.LANGUAGE],
                                                             parse_mode='HTML')))


async def evaluate_song(update):
    if update.effective_message.text:
        song_name = message_handling.user_songs[update.message.chat.id]
        message_handling.user_songs.pop(update.message.chat.id)

        msg = clean_input(update.message.text)

        song_match = round((1 - Levenshtein.distance(clean_input(strings.LYRICS[song_name]), msg)
                            / len(clean_input(strings.LYRICS[song_name]))) * 100)
        if song_match < 100:
            # TODO: Use request queue
            await update.message.reply_text(strings.LYRICS[song_name], parse_mode='HTML')

        # TODO: Use request queue
        await update.message.reply_text(strings.MATCH_TEXT[config.LANGUAGE] + str(song_match) + ' %', parse_mode='HTML',
                                        disable_web_page_preview=True)
    else:
        # TODO: Use request queue
        await update.message.reply_text(strings.UNSUPPORTED_FILE_FORMAT[config.LANGUAGE], parse_mode='HTML')


async def previous_command(update, context):
    """Command to list all previous announcements."""
    global queue_id
    command_count['previous'] = command_count['previous'] + 1

    if not is_user(update.message.chat.id):
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                            lambda: update.message.reply_text(strings.NOT_USER[config.LANGUAGE], parse_mode='HTML')))
        return

    for broadcast in get_broadcasts():
        lines = broadcast.split('\n')
        broadcast_file = None
        if lines[0][:3] == '<@|':
            broadcast_file = config.BROADCAST_FILES_DIR + '/' + lines[0].split('|')[1]
            lines = lines[1:]
        msg = '\n'.join(lines)
        if not broadcast_file:
            request_queue.put((4, get_queue_id(), update.message.chat.id,
                               lambda l_msg=msg: update.message.reply_text(l_msg, disable_web_page_preview=True,
                                                                 parse_mode='HTML')))
        elif broadcast_file.split('.')[1] == 'jpg':
            request_queue.put((4, get_queue_id(), update.message.chat.id,
                                lambda l_msg=msg, l_file=broadcast_file:
                                context.bot.send_photo(update.message.chat.id, open(l_file, 'rb'),
                                                               caption=l_msg, parse_mode='HTML')))
        elif broadcast_file.split('.')[1] == 'mp4':
            request_queue.put((4, get_queue_id(), update.message.chat.id,
                                lambda l_msg=msg, l_file=broadcast_file:
                                context.bot.send_video(update.message.chat.id, open(l_file, 'rb'),
                                                               caption=l_msg, parse_mode='HTML')))
        elif broadcast_file.split('.')[1] == 'gif':
            request_queue.put((4, get_queue_id(), update.message.chat.id,
                                lambda l_msg=msg, l_file=broadcast_file:
                                context.bot.send_animation(update.message.chat.id, open(l_file, 'rb'),
                                                                   caption=l_msg, parse_mode='HTML')))
        else:
            request_queue.put((4, get_queue_id(), update.message.chat.id,
                                lambda: update.message.reply_text(strings.UNSUPPORTED_FILE_FORMAT[config.LANGUAGE],
                                                                  parse_mode='HTML')))


async def send_broadcast(update, context, is_temp=False):
    """Broadcast a message."""
    global previous_broadcast, queue_id

    cmd_length = 11
    if is_temp:
        cmd_length = 16

    if is_moderator(update.message.chat.id):
        file_name = None
        total_sent = 0
        if not (update.message.photo or update.message.video or update.message.animation):
            if len(update.message.text) <= cmd_length:
                request_queue.put((2, get_queue_id(), update.message.chat.id,
                                   lambda: update.message.reply_text(strings.INVALID_COMMAND[config.LANGUAGE],
                                                                     parse_mode='HTML')))
                return

            # Sending text
            msg = update.message.text_html[cmd_length:]
            previous_broadcast = []
            for chat_id in get_chat_ids():
                request_queue.put((1, get_queue_id(), chat_id,
                                    lambda l_id=chat_id, l_msg=msg:
                                    context.bot.send_message(l_id, l_msg, disable_web_page_preview=True,
                                                             parse_mode='HTML')))
        else:
            file_name = next_file_name()
            msg = update.message.caption_html[cmd_length:]

            if update.message.photo:
                # Sending photo
                file_name += '.jpg'
                for chat_id in get_chat_ids():
                    file_id = update.message.photo[-1].file_id
                    new_file = await context.bot.get_file(file_id)
                    await new_file.download_to_drive(config.BROADCAST_FILES_DIR + '/' + file_name)

                    request_queue.put((1, get_queue_id(), chat_id,
                                        lambda l_id=chat_id, l_file=file_name, l_msg=msg:
                                        context.bot.send_photo(l_id, open(config.BROADCAST_FILES_DIR + '/' + l_file,
                                                                          'rb'),
                                                               caption=l_msg, parse_mode='HTML')))
            elif update.message.video:
                # Sending video
                file_name += '.mp4'
                for chat_id in get_chat_ids():
                    file_id = update.message.video.file_id
                    new_file = await context.bot.get_file(file_id)
                    await new_file.download_to_drive(config.BROADCAST_FILES_DIR + '/' + file_name)

                    request_queue.put((1, get_queue_id(), chat_id,
                                        lambda l_id=chat_id, l_file=file_name, l_msg=msg:
                                        context.bot.send_video(l_id, open(config.BROADCAST_FILES_DIR + '/'
                                                                                     + l_file, 'rb'),
                                                                       caption=l_msg, parse_mode='HTML')))
            else:
                # Sending animation
                file_name += '.gif'
                for chat_id in get_chat_ids():
                    file_id = update.message.animation.file_id
                    new_file = await context.bot.get_file(file_id)
                    await new_file.download_to_drive(config.BROADCAST_FILES_DIR + '/' + file_name)

                    request_queue.put((1, get_queue_id(), chat_id,
                                        lambda l_id=chat_id, l_file=file_name, l_msg=msg:
                                        context.bot.send_animation(l_id, open(config.BROADCAST_FILES_DIR + '/' + l_file,
                                                                              'rb'),
                                                                   caption=l_msg, parse_mode='HTML')))
            previous_broadcast = []

        if not is_temp:
            save_broadcasts(get_broadcasts(), msg, file_name)

        print("Broadcast message.")
    else:
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_ADMIN[config.LANGUAGE], parse_mode='HTML')))


async def broadcast_command(update, context):
    """Admin command to broadcast and save a message."""
    await send_broadcast(update, context, is_temp=False)


async def broadcast_temp_command(update, context):
    """Admin command to broadcast a message without saving."""
    await send_broadcast(update, context, is_temp=True)


async def broadcast_forward(bot, from_chat, original_id, msg_text=None, file_name=None, is_temp=False):
    """Broadcast a forwarded message."""
    global previous_broadcast, queue_id
    previous_broadcast = []
    for chat_id in get_chat_ids():
        request_queue.put((1, get_queue_id(), chat_id,
                            lambda l_id=chat_id: bot.forward_message(l_id, from_chat, original_id)))
    if msg_text:
        msg_text = '<b>Forwarded</b>\n-\n' + msg_text
    else:
        msg_text = '<b>Forwarded</b>'

    if not is_temp:
        save_broadcasts(get_broadcasts(), msg_text, file_name)

    message_handling.forwarding_data = (-1, 0, False)
    print("Broadcast forwarded message.")


async def edit_command(update, context):
    """Admin command to edit previous broadcast."""
    global previous_broadcast, queue_id

    cmd_length = 5

    if is_moderator(update.message.chat.id):
        msg = update.message.text_html[cmd_length:]
        for message in previous_broadcast:
            request_queue.put((2, get_queue_id(), update.message.chat.id,
                                lambda l_message=message, l_msg=msg:
                                context.bot.editMessageText(chat_id=l_message[0], message_id=l_message[1], text=l_msg,
                                                            disable_web_page_preview=True, parse_mode='HTML')))
        save_broadcasts(get_broadcasts(), msg, edit=True)
    else:
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_ADMIN[config.LANGUAGE], parse_mode='HTML')))


async def delete_command(update, context):
    """Admin command to delete previous broadcast."""
    global previous_broadcast, queue_id

    if is_moderator(update.message.chat.id):
        for message in previous_broadcast:
            request_queue.put((2, get_queue_id(), update.message.chat.id,
                                lambda l_message=message: context.bot.delete_message(l_message[0], l_message[1])))

        save_broadcasts(get_broadcasts()[:-1])
        previous_broadcast = []
    else:
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_ADMIN[config.LANGUAGE], parse_mode='HTML')))


async def forward_command(update, context):
    """Admin command to activate forwarding mode with saving."""
    if is_moderator(update.message.chat.id):
        message_handling.forwarding_data = (update.message.chat.id, time.perf_counter(), False)
    else:
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_ADMIN[config.LANGUAGE], parse_mode='HTML')))


async def forward_temp_command(update, context):
    """Admin command to activate forwarding mode without saving."""
    if is_moderator(update.message.chat.id):
        message_handling.forwarding_data = (update.message.chat.id, time.perf_counter(), True)
    else:
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_ADMIN[config.LANGUAGE], parse_mode='HTML')))


async def users_command(update, context):
    """Admin command to get number of active users."""
    if is_moderator(update.message.chat.id):
        request_queue.put((2, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text("Number of active users: " + str(len(get_chat_ids())),
                                                             parse_mode='HTML')))
    else:
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_ADMIN[config.LANGUAGE], parse_mode='HTML')))


async def update_command(update, context):
    """Admin command to update bot."""
    if time.perf_counter() - start_time < 3:  # Prevent from instantly running, creating a loop
        print("Tried updating too soon.")
        return
    if is_moderator(update.message.chat.id):
        subprocess.call("./update_bot.sh", shell=True)
        quit()
    else:
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_ADMIN[config.LANGUAGE], parse_mode='HTML')))


async def reboot_command(update, context):
    """Admin command to reboot server."""
    if time.perf_counter() - start_time < 3:  # Prevent from instantly running, creating a loop
        print("Tried rebooting too soon.")
        return
    if is_moderator(update.message.chat.id):
        subprocess.run(["sudo", "reboot"])
    else:
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_ADMIN[config.LANGUAGE], parse_mode='HTML')))


async def run_command(update, context):
    """Admin command to run commands in terminal."""
    if time.perf_counter() - start_time < 3:  # Prevent from instantly running, creating a loop
        print("Tried running command too soon.")
        return
    if is_moderator(update.message.chat.id):
        print("No command to run")
        # subprocess.run(["source", "env/bin/activate"], shell=True)
        # subprocess.run(["pip", "install", "-r", "requirements.txt"], shell=True)
    else:
        request_queue.put((4, get_queue_id(), update.message.chat.id,
                           lambda: update.message.reply_text(strings.NOT_ADMIN[config.LANGUAGE], parse_mode='HTML')))


async def error_handler(update, context):
    """Send error messages to admins."""
    global queue_id

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    error_message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    for admin_id in config.BOT_ADMINS:
        for chunk in [error_message[i:i + 4096] for i in range(0, len(error_message), 4096)]:
            request_queue.put((2, get_queue_id(), admin_id,
                                lambda l_id=admin_id, l_chunk=chunk:
                                context.bot.send_message(l_id, l_chunk, disable_web_page_preview=True)))


async def weekly_reboot(context):
    if time.perf_counter() - start_time < 60:  # Prevent from running multiple times within a minute
        print("Tried rebooting too soon.")
        return
    for admin_id in config.BOT_ADMINS:
        await context.bot.send_message(chat_id=admin_id, text="Bot rebooting...")
    subprocess.run(["sudo", "reboot"])


async def weekly_backup(context):
    if time.perf_counter() - start_time < 60:  # Prevent from running multiple times within a minute
        print("Tried backing up too soon.")
        return
    for admin_id in config.BOT_ADMINS:
        await context.bot.send_message(chat_id=admin_id, text="Commands handled since last update: " + str(command_count))
        await context.bot.send_message(chat_id=admin_id, text="Bot backing up...")
    subprocess.call("./update_bot.sh", shell=True)
    quit()


async def weekly_backup_message(context):
    global queue_id

    for admin_id in config.BOT_ADMINS:
        request_queue.put((2, get_queue_id(), admin_id,
                            lambda l_id=admin_id: context.bot.send_message(chat_id=l_id, text="Bot running...")))


async def run_requests(context):
    """Run queued requests with cooldown."""
    global queue_id, broadcasts_sent

    function_chats = {}
    while request_queue.qsize() > 0:
        first_data = request_queue.get()
        if (function_chats.get(first_data[2], 0) >= max_instant_requests_personal
                or len(function_chats.keys()) >= max_instant_requests):
            request_queue.put((0, first_data[1], first_data[2], lambda: first_data[3]()))
            break
        function_chats[first_data[2]] = function_chats.get(first_data[2], 0) + 1
        try:
            sent = await first_data[3]()
            if first_data[0] == 1:  # Pin broadcast messages
                await context.bot.pin_chat_message(sent.chat.id, sent.message_id, disable_notification=True)
                previous_broadcast.append((sent.chat.id, sent.message_id))
                broadcasts_sent += 1
                print("Broadcast sent to", sent.chat.id)
        except:
            print("Function call", first_data, "unsuccessful.")

    if request_queue.qsize() == 0:
        queue_id = 0
        if broadcasts_sent > 0:
            for admin_id in config.BOT_ADMINS:
                request_queue.put((2, get_queue_id(), admin_id,
                                    lambda l_id=admin_id: context.bot.send_message(l_id, "Broadcast sent to "
                                                                                   + str(broadcasts_sent) + " users.",
                                                                                   disable_web_page_preview=True,
                                                                                   parse_mode='HTML')))
            broadcasts_sent = 0


def main():
    """Initialize bot with command handlers."""

    # Command initialization
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('info', info_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler(strings.SONG_COMMAND[config.LANGUAGE], song_command))
    application.add_handler(CommandHandler(strings.FACT_COMMAND[config.LANGUAGE], fact_command))
    application.add_handler(CommandHandler(strings.PREVIOUS_COMMAND[config.LANGUAGE], previous_command))
    application.add_handler(CommandHandler('exit', exit_command))

    application.add_handler(CommandHandler('broadcast', broadcast_command))
    application.add_handler(CommandHandler('broadcast_temp', broadcast_temp_command))
    application.add_handler(CommandHandler('edit', edit_command))
    application.add_handler(CommandHandler('delete', delete_command))
    application.add_handler(CommandHandler('forward', forward_command))
    application.add_handler(CommandHandler('forward_temp', forward_temp_command))
    application.add_handler(CommandHandler('users', users_command))
    application.add_handler(CommandHandler('update_bot', update_command))
    application.add_handler(CommandHandler('reboot_server', reboot_command))
    application.add_handler(CommandHandler('run', run_command))

    # Sending messages to bot. Order matters here.
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE, message_handling.send_from_private))
    application.add_handler(MessageHandler(filters.REPLY, message_handling.reply))

    # Add scheduled tasks.
    # application.job_queue.run_daily(weekly_reboot, time=datetime.time(3 - 2, 50, 0), days=[0], name="Weekly reboot")
    application.job_queue.run_daily(weekly_backup, time=datetime.time(4 - 2, 0, 0), days=[0], name="Weekly backup")
    application.job_queue.run_daily(weekly_backup_message, time=datetime.time(4 - 2, 5, 0), days=[0],
                                    name="Weekly backup message")
    application.job_queue.run_repeating(run_requests, interval=request_cooldown)

    # application.add_error_handler(error_handler)   # TODO: Fix error handler to continue function

    # Run bot
    application.run_polling(1.0)


if __name__ == '__main__':
    start_time = time.perf_counter()  # Set script starting time
    main()
