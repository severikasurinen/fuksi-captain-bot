"""
A file that contains all the messaging functionalities.
"""

import main_script
import config
import strings
import time
import datetime


sent_messages = {}
user_songs = {}
forwarding_data = (-1, 0, False)


def clear_messages():
    global sent_messages

    sent_messages = {}


async def robust_send_message(bot, msg, to, reply_id, pseudonym=None):
    """A robust method for forwarding different types of messages anonymously"""

    sent = None
    if pseudonym:
        pseudonym_text = '- ' + pseudonym
    else:
        pseudonym_text = ''

    if msg.text:
        sent = await bot.send_message(chat_id=to, text=msg.text_html + '\n\n' + pseudonym_text,
                                      reply_to_message_id=reply_id, parse_mode='HTML')
    elif msg.sticker:
        sent = await bot.send_sticker(to, msg.sticker.file_id, reply_to_message_id=reply_id)
    elif msg.photo:
        if msg.caption:
            capt = msg.caption_html + '\n\n' + pseudonym_text
        else:
            capt = pseudonym_text
        sent = await bot.send_photo(to, msg.photo[0].file_id, caption=capt,
                                    reply_to_message_id=reply_id, parse_mode='HTML')
    elif msg.video:
        if msg.caption:
            capt = msg.caption_html + '\n\n' + pseudonym_text
        else:
            capt = pseudonym_text
        sent = await bot.send_video(to, msg.video.file_id, caption=capt,
                                    reply_to_message_id=reply_id, parse_mode='HTML')
    elif msg.animation:
        if msg.caption:
            capt = msg.caption_html + '\n\n' + pseudonym_text
        else:
            capt = pseudonym_text
        sent = await bot.send_animation(to, msg.animation.file_id, caption=capt,
                                        reply_to_message_id=reply_id, parse_mode='HTML')
    elif msg.video_note:
        sent = await bot.send_video_note(to, msg.video_note.file_id, reply_to_message_id=reply_id)
    elif msg.document:
        sent = await bot.send_document(to, msg.document.file_id, reply_to_message_id=reply_id)
    elif msg.voice:
        sent = await bot.send_voice(to, msg.voice.file_id, reply_to_message_id=reply_id)
    elif msg.audio:
        sent = await bot.send_audio(to, msg.audio.file_id, reply_to_message_id=reply_id)
    elif msg.location:
        sent = await bot.send_location(to, location=msg.location, reply_to_message_id=reply_id)
    else:
        await bot.send_message(msg.chat.id, strings.UNSUPPORTED_FILE_FORMAT[config.LANGUAGE])

    return sent


async def send_from_private(update, context):
    """Forward a private message sent for the bot to the receiving chat anonymously"""
    msg = update.effective_message
    if msg.from_user.is_bot:
        return
    if ((not msg.caption or msg.caption[:10] == '/broadcast' or msg.caption[0] != '/')
            and (not msg.text or msg.text[0] != '/')):
        if main_script.is_moderator(msg.from_user.id) and msg.caption and msg.caption[:11] == '/broadcast ':
            await main_script.broadcast_command(update, context)
        elif (forwarding_data[0] == msg.from_user.id and time.perf_counter() - forwarding_data[1]
              <= main_script.forwarding_timeout and msg.forward_date):
            if msg.text:
                msg_text = msg.text_html
            elif msg.caption:
                msg_text = msg.caption_html
            else:
                msg_text = None

            if msg.photo or msg.video or msg.animation:
                if msg.photo:
                    file_name = main_script.next_file_name() + '.jpg'
                    file_id = update.message.photo[-1].file_id
                elif msg.video:
                    file_name = main_script.next_file_name() + '.mp4'
                    file_id = update.message.video.file_id
                else:
                    file_name = main_script.next_file_name() + '.gif'
                    file_id = update.message.animation.file_id

                new_file = await context.bot.get_file(file_id)
                await new_file.download_to_drive(config.BROADCAST_FILES_DIR + '/' + file_name)
            else:
                file_name = None

            await main_script.broadcast_forward(context.bot, msg.chat.id, msg.message_id, msg_text, file_name,
                                                is_temp=forwarding_data[2])
        elif update.message.chat.id in user_songs:
            await main_script.evaluate_song(update)
        else:
            if msg.forward_date is None:
                if msg.sticker or msg.animation:
                    is_spam = True
                    temp_users = main_script.get_temp_users()
                    if (msg.from_user.id in temp_users.keys() and temp_users[msg.from_user.id][2] == 'S' and
                            (datetime.datetime.now() - temp_users[msg.from_user.id][0]).seconds
                            / 60 < main_script.spam_cooldown):
                        # TODO: Use request queue
                        await update.message.reply_text(strings.SPAM[config.LANGUAGE], parse_mode='HTML')
                        return
                else:
                    is_spam = False

                #TODO: Use request queue
                sent = await robust_send_message(context.bot, msg, config.MESSAGING_CHAT, None,
                                                                            main_script.add_temp_user(msg.from_user.id,
                                                                                                      spam=is_spam))
                sent_messages[sent.message_id] = (msg.chat.id, msg.message_id)
            else:
                # TODO: Use request queue
                sent = await context.bot.forward_message(config.MESSAGING_CHAT, msg.chat.id, msg.message_id)
                sent_messages[sent.message_id] = (msg.chat.id, msg.message_id)
    else:
        # TODO: Use request queue
        await update.message.reply_text(strings.INVALID_COMMAND[config.LANGUAGE], parse_mode='HTML')


async def reply(update, context):
    """Forward reply from receiving chat back to the original sender"""

    msg_id = update.effective_message.reply_to_message.message_id
    if msg_id in sent_messages:
        org = sent_messages[msg_id]
        # TODO: Use request queue
        await robust_send_message(context.bot, update.effective_message, org[0], org[1])
