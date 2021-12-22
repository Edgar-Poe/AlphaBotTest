from django.core.management.base import BaseCommand

from tgbot.models import AnswerFromChat, ChatInUse, MessageFromBotInChat

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class Command(BaseCommand):

    def handle(self, *args, **options):

        import telebot
        bot = telebot.TeleBot('5058102833:AAEe1_lZcuRN7S0g-xcrp51rWBwlKPaxF-Q')

        def set_stage(stage_name: str, tg_message):
            chat, created = ChatInUse.objects.get_or_create(
                chat_id=tg_message.chat.id,
                defaults={'stage': stage_name})
            chat.stage = stage_name
            chat.save()


        @bot.message_handler(commands=['start'])
        def start_message(message):
            print(message)
            chat_obj, created = ChatInUse.objects.get_or_create(
                chat_id=message.chat.id,
                defaults={'stage': 'new'})
            if not created:
                chat_obj.save()

            messages_in_that_chat = MessageFromBotInChat.objects.filter(from_chat=chat_obj)
            if messages_in_that_chat:
                for one_message_in_base in messages_in_that_chat:
                    try:
                        bot.delete_message(one_message_in_base.from_chat.chat_id, one_message_in_base.message_id)
                    except:
                        pass
                    one_message_in_base.delete()

            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text='Пройти анкету', callback_data='start_quiz'))

            MessageFromBotInChat(message_id=
                                 bot.send_message(chat_id=message.chat.id,
                                                  text="Приветственное сообщение!",
                                                  reply_markup=markup).message_id,
                                 from_chat=
                                 ChatInUse.objects.get(chat_id=
                                                       message.chat.id)).save()
            # save message_id and chat_id in database for delete in future

        @bot.message_handler(content_types=['text'])
        def message_handler(message):
            print(message)
            chat_obj, created = ChatInUse.objects.get_or_create(
                chat_id=message.chat.id,
                defaults={'stage': 'new'})
            if chat_obj.stage == 'quiz_started':
                print('name = ' + message.text)
                chat_obj.presaved_name = message.text
                chat_obj.save()
                set_stage('name_set', message)

                MessageFromBotInChat(message_id=
                                     bot.send_message(message.chat.id, 'Введите Ваш номер телефона').message_id,
                                     from_chat=ChatInUse.objects.get(chat_id=message.chat.id)).save()

            if chat_obj.stage == 'name_set':
                print('phone = ' + message.text)
                chat_obj.presaved_phone = message.text
                chat_obj.save()
                set_stage('phone_set', message)

                default_markup = telebot.types.InlineKeyboardMarkup()
                default_markup.add(telebot.types.InlineKeyboardButton(text='Вариант №1', callback_data='On_choise1'))
                default_markup.add(telebot.types.InlineKeyboardButton(text='Вариант №2', callback_data='On_choise2'))
                default_markup.add(telebot.types.InlineKeyboardButton(text='Вариант №3', callback_data='On_choise3'))
                default_markup.add(telebot.types.InlineKeyboardButton(text='Отправить', callback_data='Apply'))

                bot.send_message(message.chat.id, 'Выберите один или несколько вариантов ответа:', reply_markup=default_markup)

        @bot.callback_query_handler(func=lambda call: True)
        def query_handler(call):
            bot.answer_callback_query(callback_query_id=call.id, text='Кнопочки, мм.. ')

            if call.data == 'start_quiz':

                MessageFromBotInChat(message_id=
                                     bot.send_message(call.message.chat.id, 'Введите Ваше имя').message_id,
                                     from_chat=ChatInUse.objects.get(chat_id=call.message.chat.id)).save()
                set_stage('quiz_started', call.message)
                # save message_id as start_quiz and chat id in stage
            if 'choise' in call.data:
                position, chosen_button = call.data.split('_')
                upd_markup = telebot.types.InlineKeyboardMarkup()
                for inline_button in call.message.reply_markup.keyboard:
                    if call.data == inline_button[0].callback_data:
                        if position == 'On':
                            upd_markup.add(telebot.types.InlineKeyboardButton(
                                text='✅ ' + inline_button[0].text,
                                callback_data='Off_' + chosen_button))
                        elif position == 'Off':
                            upd_markup.add(telebot.types.InlineKeyboardButton(
                                text=inline_button[0].text[2:],
                                callback_data='On_' + chosen_button))

                    else:
                        upd_markup.add(telebot.types.InlineKeyboardButton(text=inline_button[0].text,
                                                                          callback_data=inline_button[0].callback_data))
                bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.id, reply_markup=upd_markup)

            if call.data == 'Apply':
                answers_list = []
                for inline_button in call.message.reply_markup.keyboard:
                    if inline_button[0].callback_data.split('_')[0] == 'Off':
                        answers_list.append(inline_button[0].text[2:])
                if not answers_list:
                    MessageFromBotInChat(message_id=
                                         bot.send_message(call.message.chat.id,
                                                          'Выберите, хотя бы один вариант ответа.').message_id,
                                         from_chat=ChatInUse.objects.get(chat_id=call.message.chat.id)).save()
                else:
                    #print(str(answers_list))
                    #bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.id)
                    bot.delete_message(call.message.chat.id, call.message.id)
                    this_chat_from_db = ChatInUse.objects.get(chat_id=call.message.chat.id)
                    def list_to_string(list):
                        string = ''
                        for elem in list:
                            string += str(elem)
                            string+= ', '
                        else:
                            if string:
                                string = string[0:-2]
                        return string
                    answers_list = list_to_string(answers_list)
                    print(this_chat_from_db.chat_id, call.message.chat.username, this_chat_from_db.presaved_name, this_chat_from_db.presaved_phone, answers_list)

                    AnswerFromChat(chat_id=this_chat_from_db.chat_id, tg_login=call.message.chat.username,
                                   name=this_chat_from_db.presaved_name, phone=this_chat_from_db.presaved_phone,
                                   answers=answers_list).save()

                    # GOOGLE ------------------------------------
                    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
                    creds = Credentials.from_authorized_user_file('tgbot/management/commands/token.json', SCOPES)
                    SAMPLE_SPREADSHEET_ID = '1zlmW9gWXBSJVpnE87nK84f2bZPuQ_-glfOSLYITxieY'
                    SAMPLE_RANGE_NAME = 'A1:F1'
                    try:
                        service = build('sheets', 'v4', credentials=creds)

                        values = [[this_chat_from_db.chat_id, call.message.chat.username,
                                   this_chat_from_db.presaved_name, this_chat_from_db.presaved_phone,
                                   answers_list]]
                        body = {
                            'values': values
                        }
                        result = service.spreadsheets().values().append(
                            spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
                            valueInputOption='RAW', body=body).execute()
                        print(result)

                    except HttpError as err:
                        print(err)

                    # GOOGLE ------------------------------------

                    bot.send_message(call.message.chat.id, 'Благодарю за ответ.')

                    chat_in_base = ChatInUse.objects.get(chat_id=call.message.chat.id)
                    messages_in_that_chat = MessageFromBotInChat.objects.filter(from_chat=chat_in_base)
                    for one_message_in_base in messages_in_that_chat:
                        try:
                            bot.delete_message(one_message_in_base.from_chat.chat_id, one_message_in_base.message_id)
                        except:
                            pass
                    chat_in_base.delete()

        bot.polling(none_stop=True)
