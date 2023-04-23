import pandas as pd
import requests


def get_file_of_tg(id, token):
    zap = f'''https://api.telegram.org/bot{token}/getFile?file_id={id}'''
    response = requests.get(zap).json()["result"]["file_path"]
    dls = f'https://api.telegram.org/file/bot{token}/{response}'
    resp = requests.get(dls)
    output = open('dow.xlsx', 'wb')
    output.write(resp.content)
    output.close()


def sendMessage(id, text, token):
    zap = f'''https://api.telegram.org/bot{token}/sendMessage'''
    params = {'chat_id': id, 'text': text}
    return requests.get(zap, params=params).json()


def check_file_of_tg():
    a = [['ID', 'ФИО', 'Должность(1-админ, 0-клиент', 'ID TG', 'UserName'],
         ['ID Категории', 'Название категории', 'Путь к файлу картинки'],
         ['Сообщение', 'Дата отправления'],
         ['Вопрос', 'Ответ'],
         ['Название', 'Описание']]
    flag = True
    for sheet in range(5):
        df = pd.read_excel(io='dow.xlsx', sheet_name=sheet)
        if ''.join(df.head(0).columns.values) != ''.join(a[sheet]):
            flag = False
            break
    return flag
