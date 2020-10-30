import telebot
import config
import re
import json
import string
import datetime

bot = telebot.TeleBot(config.TOKEN)

# Проверка даты на корректность
def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%d-%m-%Y')
        return True
    except ValueError:
        return False

#Добавление записи в json "БД"
def Add(message,user_id):
    #Нормализуем текст сообщения
    message_text = message.text
    message_text = message_text.replace('add','')
    message_text = message_text.replace('Add', '')
    message_text = message_text.replace('.', '-')
    message_list = message_text.split(',')

    # Проверка даты на корректность
    if(validate(message_list[0].replace(' ','')) == False):
        return "Дата введена некорректно"

    #Заполняем словарь
    json_list ={str(user_id)+'_'+str(message.message_id):{
        'Дата':message_list[0],
        'Упражнение':message_list[1],
        'Подходы':message_list[2],
        'Повторения':message_list[3]
    },}
    # Проверяем указан ли вес
    try:
        if(message_list[4]!= None):
            json_list[str(user_id)+'_'+str(message.message_id)].update({'Вес':message_list[4]})
    except IndexError:
        pass

    # Открываем файл для записи
    with open('Timetable.json', 'r', encoding='utf-8') as f:
        json_file = json.load(f)

    # Редактируем json
    json_file.update(json_list)

    # Сохраняем файл
    with open("Timetable.json", "w", encoding='utf-8') as write_file:
        json.dump(json_file, write_file, ensure_ascii=False)
    return "Данные записаны"


#Показать все записи конкретного пользователя
def Show(user_id):
    all_text = ''
    #Загружаем json файл
    with open('Timetable.json', 'r', encoding='utf-8') as f:
        json_file = json.load(f)
    #Формирование строки
    for header in json_file.keys():
        if(header.find(str(user_id))!=-1):
            all_text += 'Дата:'+json_file[header]['Дата']+'\n'+'Упражнение:'+json_file[header]['Упражнение']+'\n'+'Подходы:'+json_file[header]['Подходы']+'\n'
            #Проверка на наличие поля "Вес"
            try:
                if(json_file[header]['Вес']!= None):
                    all_text += 'Вес:'+json_file[header]['Вес']+'\n\n'
            except KeyError:
                all_text += '\n'
    if(all_text == ''):
        return "Извините, вы не сделали еще ни одной записи"
    return all_text



def Show_date(user_id,message):
    # Получаем дату из текста
    text = re.sub("\s+", " ", message.text)
    date = text.split(' ')
    date = date[1]
    date = date.replace('.', '-')
    all_text = ''

    # Проверка даты на корректность
    if(validate(date) == False):
        return "Дата введена некорректно"

    # Загружаем json файл
    with open('Timetable.json', 'r', encoding='utf-8') as f:
        json_file = json.load(f)
    # Формирование строки
    for header in json_file.keys():
        if(header.find(str(user_id))!=-1):
            if(date == json_file[header]['Дата'].replace(' ','')):
                all_text += 'Дата:'+json_file[header]['Дата']+'\n'+'Упражнение:'+json_file[header]['Упражнение']+'\n'+'Подходы:'+json_file[header]['Подходы']+'\n'
                # Проверка на наличие поля "Вес"
                try:
                    if(json_file[header]['Вес']!= None):
                        all_text += 'Вес:'+json_file[header]['Вес']+'\n\n'
                except KeyError:
                    all_text += '\n'
    if(all_text == ''):
        return "Извините, в заданную дату нет записей"
    return all_text


#Удаление всех записей конкретного пользователя
def Delete(user_id):
    # Загружаем json файл
    with open('Timetable.json', 'r', encoding='utf-8') as f:
        json_file = json.load(f)
    # Ищем данные по Id
    for header in list(json_file):
        if (header.find(str(user_id)) != -1):
            json_file.pop(header) #Удаление по ключу
    #Сохраняем json
    with open("Timetable.json", "w", encoding='utf-8') as write_file:
        json.dump(json_file, write_file, ensure_ascii=False)
    return "Таблица очищена"


#Удаление данных пользователя по дате
def Delete_date(user_id,message):
    # Получаем дату из сообщения
    text = re.sub("\s+", " ", message.text)
    date = text.split(' ')
    date = date[1]
    date = date.replace('.', '-')

    # Проверка даты на корректность
    if(validate(date) == False):
        return "Дата введена некорректно"
    
    # Открываем json файл
    with open('Timetable.json', 'r', encoding='utf-8') as f:
        json_file = json.load(f)
    # Ищем данные по Id и дате
    for header in list(json_file):
        if (header.find(str(user_id)) != -1):
            if(date == json_file[header]['Дата'].replace(' ','')):
                json_file.pop(header)# Удаление по ключу
    # Сохраняем json
    with open("Timetable.json", "w", encoding='utf-8') as write_file:
        json.dump(json_file, write_file, ensure_ascii=False)
    return "Данные на "+date+" удалены"

@bot.message_handler(commands=['start'])
def welcome(message):
    # Приветствие
    sticker = open('static/welcome.webp','rb')
    bot.send_sticker(message.chat.id, sticker)
    bot.send_message(message.chat.id, "Бот создан для записи результатов тренировок\nКоманды:\n1)help\n2)add dd.mm.yy(yy), упражнение, подходы, повторения, вес(опционально)\n3)show\n4)show dd.mm.yyyy\n5)delete\n6)delete dd.mm.yyyy")

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    if message.chat.type == 'private':

        #Приветы
        if(re.search(r'(П|п)ривет|(З|з)дравствуй|(Х|х)ей|(Х|х)елло|(H|h)ello',message.text) != None):
            bot.send_message(message.chat.id, "Привет")

        #Хелп
        elif(re.search(r'(h|H)elp',message.text) !=None):
            bot.send_message(message.chat.id, "Команды:\n1)help\n2)add dd.mm.yy(yy), упражнение, подходы, повторения, вес(опционально)\n3)show\n4)show dd.mm.yyyy\n5)delete\n6)delete dd.mm.yyyy")

        #Добавление записи
        elif(re.search(r'(A|a)dd',message.text) !=None):
            if(re.search(r'(A|a)dd\s+\d{2}\.\d{2}\.\d{4}\s*,\s*(\w+\s*)+,\s*\d+,\s*\d+,?\s*(\d+)\s*',message.text) !=None):
                bot.send_message(message.chat.id, Add(message, message.from_user.id))
            else:
                bot.send_message(message.chat.id, "Команда добавления введена неверно\nФормат ввода:\nadd dd.mm.yy(yy), упражнение, подходы, повторения, вес(опционально)")

        #Показать запись по дате
        elif(re.search(r'(S|s)how\s+\d{2}\.\d{2}\.\d{4}\s*',message.text) !=None):
            bot.send_message(message.chat.id, Show_date(message.from_user.id,message))

        #Показать все записи
        elif(re.search(r'(S|s)how',message.text) !=None):
            bot.send_message(message.chat.id, Show(message.from_user.id))

        #Удалить все записи пользователя по дате
        elif(re.search(r'(D|d)elete\s+\d{2}\.\d{2}\.\d{4}\s*',message.text) !=None):
            bot.send_message(message.chat.id, Delete_date(message.from_user.id,message))

        # Удалить все записи пользователя
        elif(re.search(r'(D|d)elete',message.text) !=None):
            bot.send_message(message.chat.id, Delete(message.from_user.id))
        else:
            bot.send_message(message.chat.id, "Ключевые слова не найдены")



if __name__ == '__main__':
    bot.polling(none_stop=True)