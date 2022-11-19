# Импортируем необходимые библиотеки
import json
import requests
import telebot
from telebot import types

# Вставляем API токен с сайта dadata.ru
API_KEY = 'API токен'
# Используем базовый URL для запросов
BASE_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/'


# Вводим функцию поиска юридических лиц или индивидуаьных предпринимателей
def find_company(resource, query):
    url = BASE_URL + resource
    headers = {
        'Authorization': 'Token ' + API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {
        'query': query
    }
    res = requests.post(url, data=json.dumps(data), headers=headers)
    return res.json()


# Создаем экземпляр Telegram-бота и указываем токен (полученный от @BotFather)
TOKEN = 'TOKEN'
bot = telebot.TeleBot(TOKEN)


# Функция, обрабатывающая команду /start
@bot.message_handler(commands=['start'])
def welcome(message):
    text = '''Добро пожаловать!
    Бот предназначен для поиска основной информации по ЮЛ и ИП.
    Информация для ИП включает:
    - наименование;
    - ИНН;
    - ОГРН;
    - адрес.

    Информация для ЮЛ включает:
    - сокращенное и полное наименование;
    - ОГРН; ИНН; КПП;
    - информация о руководителе;
    - прямую ссылку на проверку наличия лицензий Ростехнадзора в ОИАЭ;
    - прямую ссылку на проверку наличия лицензии Роспотребнадзора.
    Для осушествления поиска введите ИНН или ОГРН (или ОГРИП) или наименование ЮЛ (или ИП).
   '''
    bot.send_message(message.chat.id, text=text, parse_mode='html')


# Функция, обрабатывающая команду /help
@bot.message_handler(commands=['help'])
def helper(message):
    text = '''Для поиска введите ИНН или ОГРН (или ОГРИП) или наименование ЮЛ (или ИП).

    Для ИП в РФ действуют следующие форматы:
    - ИНН последовательность из 12 цифр;
    - ОГРНИП последовательность из 15 цифр.
    
    Для ЮЛ в РФ действуют следующие форматы:
    - ИНН последовательность из 10 цифр;
    - ОГРН последовательность из 13 цифр.
    
    Надеюсь все понятно. Успехов в поиске!
    '''
    bot.send_message(message.chat.id, text=text, parse_mode='html')


# Получаем сообщение от пользователя
@bot.message_handler(content_types=['text'])
def find_org(message):
    # Осуществляем поиск
    data = find_company('party', message.text)
    # Определяем количество найденных ЮЛ и ИП
    amount_sum = len(data['suggestions'])
    # Осуществляем проверку, если количество найденных ЮЛ и ИП больше 1
    if amount_sum > 1:
        count_org = 0
        inn_list = []
        # Отправляем сообщение пользователю по количеству найденных позиций
        bot.send_message(message.chat.id, 'Найдено совпадений: {}'.format(amount_sum))
        # Отправляем пользователю все найденные результаты в сокращенной форме
        for i in range(amount_sum):
            p = i + 1
            text_0 = str(p) + '. ' + data['suggestions'][i]['value'] \
                + '\n' + 'ИНН: ' + data['suggestions'][i]['data']['inn'] \
                + '\n' + 'ОГРН: ' + data['suggestions'][i]['data']['ogrn']
            bot.send_message(message.chat.id, text_0)
            # Определяем количество ЮЛ из найденного
            if len(data['suggestions'][i]['data']['inn']) == 10:
                k = i
                count_org += 1
                inn_list.append(data['suggestions'][i]['data']['inn'])
            else:
                pass
        # Отправляем пользователю информацию о количестве ЮЛ из найденного
        bot.send_message(message.chat.id, 'Количество ЮЛ: {}'.format(count_org))
        # Определяем максимальное число совпадений по ИНН для ЮЛ,
        # так определим количество филиалов ЮЛ.
        inn_set = set(inn_list)
        list_len = len(inn_list)
        list_set = len(inn_set)
        if list_len > list_set and list_len != 0:
            inn_filial = max(inn_set, key=lambda x: inn_list.count(x))
            bot.send_message(message.chat.id, 'Обнаружены Филиалы ЮЛ с ИНН: ' + inn_filial)
        else:
            pass

        # Если одно ЮЛ из найденного или обнаружены Филиалы ЮЛ по одному запросу,
        # тогда отправляем пользователю полную информацию по нему.
        if len(inn_set) == 1:
            bot.send_message(message.chat.id, '<< По ЮЛ следующая информация >>')
            # Определяем основные парметры к выдаче по ЮЛ
            name = data['suggestions'][0]['value']
            full_name = data['suggestions'][0]['data']['name']['full_with_opf']
            ogrn = data['suggestions'][0]['data']['ogrn']
            inn = data['suggestions'][0]['data']['inn']
            kpp = data['suggestions'][0]['data']['kpp']
            management_txt = data['suggestions'][0]['data']['management']['post']
            management_name = data['suggestions'][0]['data']['management']['name']
            address = data['suggestions'][0]['data']['address']['unrestricted_value']
            # Определяем ссылки по лицензиям Ростехнадзора и Роспотребнадзора
            url_1 = 'https://www.gosnadzor.ru/service/list/reestr_licences_170fz/?orgName=&inn=' \
                + inn + '&licNum=&ogrn=&licAct='
            url_2 = 'https://fp.rospotrebnadzor.ru/licen/?oper=search&numb=&firmget_name=&ogrn_inn_nza=' \
                + inn
            url_3 = 'http://fp.crc.ru/licenfr/?oper=s&type=max&text_prodnm=&text_ff_firm=&text_label=' \
                + inn
            # Прописываем текст к отправке пользователю
            text_1 = 'Сокращенное наименование: ' + name
            text_2 = 'Полное наименование: ' + full_name
            text_3 = 'ОГРН: ' + ogrn
            text_4 = 'ИНН: ' + inn
            text_5 = 'КПП: ' + kpp
            text_6 = management_txt + ': ' + management_name
            text_7 = 'Адрес юридического лица: ' + address
            text_8 = 'Посмотреть Лицензии Ростехнадзора в области использования атомной энергии'
            text_9 = 'Посмотреть Лицензии Роспотребнадзора (выданных в электронном виде)'
            text_10 = 'Посмотреть Лицензии Роспотребнадзора (выданных на бумажном носителе)'
            # Отправляем сообщение пользователю
            bot.send_message(message.chat.id, text_1 + '\n' + text_2)
            bot.send_message(message.chat.id, text_3 + '\n' + text_4 + '\n' + text_5)
            bot.send_message(message.chat.id, text_6)
            bot.send_message(message.chat.id, text_7)
            # Создаем 1 кнопку с url-ссылкой на сайт Ростехнадзора и отправляем сообщение
            markup1 = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("Лицензии Ростехнадзора", url_1)
            markup1.add(button1)
            bot.send_message(message.chat.id, text_8, reply_markup=markup1)
            # Создаем 2 кнопку с url-ссылкой на сайт Роспотребнадзора и отправляем сообщение
            markup2 = types.InlineKeyboardMarkup()
            button2 = types.InlineKeyboardButton("Лицензии Роспотребнадзора", url_2)
            markup2.add(button2)
            bot.send_message(message.chat.id, text_9, reply_markup=markup2)
            # Создаем 3 кнопку с url-ссылкой на сайт Роспотребнадзора и отправляем сообщение
            markup3 = types.InlineKeyboardMarkup()
            button3 = types.InlineKeyboardButton("Лицензии Роспотребнадзора", url_3)
            markup3.add(button3)
            bot.send_message(message.chat.id, text_10, reply_markup=markup3)
        # Отправляем сообщение пользователю в случае, если ЮЛ больше 1
        else:
            bot.send_message(message.chat.id, 'Уточните запрос, указав ИНН или ОГРН')
    # Если найден один результат по запросу
    elif amount_sum == 1:
        # Определяем основные параметры к выдаче
        name = data['suggestions'][0]['value']
        inn = data['suggestions'][0]['data']['inn']
        ogrn = data['suggestions'][0]['data']['ogrn']
        address = data['suggestions'][0]['data']['address']['unrestricted_value']
        # Если по критерию ИНН 12 символов, тогда отправляем информацию по ИП
        if len(inn) == 12:
            text_ind = name + '\n' + 'ИНН ИП: ' + inn + '\n' + 'ОГРНИП: ' + ogrn \
                + '\n' + 'Адрес ИП: ' + address
            bot.send_message(message.chat.id, text_ind)
        # Если по критерию ИНН 10 символов, тогда отправляем информацию по ЮЛ
        elif len(inn) == 10:
            # Определяем остальные параметры к выдаче
            full_name = data['suggestions'][0]['data']['name']['full_with_opf']
            kpp = data['suggestions'][0]['data']['kpp']
            management_txt = data['suggestions'][0]['data']['management']['post']
            management_name = data['suggestions'][0]['data']['management']['name']
            # Определяем ссылки по лицензиям Ростехнадзора и Роспотребнадзора
            url_1 = 'https://www.gosnadzor.ru/service/list/reestr_licences_170fz/?orgName=&inn=' \
                + inn + '&licNum=&ogrn=&licAct='
            url_2 = 'https://fp.rospotrebnadzor.ru/licen/?oper=search&numb=&firmget_name=&ogrn_inn_nza=' \
                + inn
            url_3 = 'http://fp.crc.ru/licenfr/?oper=s&type=max&text_prodnm=&text_ff_firm=&text_label=' \
                + inn
            # Прописываем текст к отправке пользователю
            text_1 = 'Сокращенное наименование: ' + name
            text_2 = 'Полное наименование: ' + full_name
            text_3 = 'ОГРН: ' + ogrn
            text_4 = 'ИНН: ' + inn
            text_5 = 'КПП: ' + kpp
            text_6 = management_txt + ': ' + management_name
            text_7 = 'Адрес юридического лица: ' + address
            text_8 = 'Посмотреть Лицензии Ростехнадзора в области использования атомной энергии'
            text_9 = 'Посмотреть Лицензии Роспотребнадзора (выданных в электронном виде)'
            text_10 = 'Посмотреть Лицензии Роспотребнадзора (выданных на бумажном носителях)'

            # Отправляем сообщение пользователю
            bot.send_message(message.chat.id, text_1 + '\n' + text_2)
            bot.send_message(message.chat.id, text_3 + '\n' + text_4 + '\n' + text_5)
            bot.send_message(message.chat.id, text_6)
            bot.send_message(message.chat.id, text_7)
            # Создаем 1 кнопку с url-ссылкой на сайт Ростехнадзора и отправляем сообщение
            markup1 = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("Лицензии Ростехнадзора", url_1)
            markup1.add(button1)
            bot.send_message(message.chat.id, text_8, reply_markup=markup1)
            # Создаем 2 кнопку с url-ссылкой на сайт Роспотребнадзора и отправляем сообщение
            markup2 = types.InlineKeyboardMarkup()
            button2 = types.InlineKeyboardButton("Лицензии Роспотребнадзора", url_2)
            markup2.add(button2)
            bot.send_message(message.chat.id, text_9, reply_markup=markup2)
            # Создаем 3 кнопку с url-ссылкой на сайт Роспотребнадзора и отправляем сообщение
            markup3 = types.InlineKeyboardMarkup()
            button3 = types.InlineKeyboardButton("Лицензии Роспотребнадзора", url_3)
            markup3.add(button3)
            bot.send_message(message.chat.id, text_10, reply_markup=markup3)
        else:
            pass
    # Если резудьтаты не найдены отправляем сообщение о повторе запроса
    else:
        bot.send_message(message.chat.id, 'Организация и ИП не найдены. Повторите запрос.')


# Запускаем бота
bot.infinity_polling()
