import sqlite3

import xlsxwriter
import pandas as pd


def createBD():  # инициализация класса
    con = sqlite3.connect('database.db', check_same_thread=False)  # подключение БД
    question_answer = """CREATE TABLE IF NOT EXISTS question_answer (
        key_words STRING NOT NULL,
        answer    STRING NOT NULL);"""

    users = """CREATE TABLE IF NOT EXISTS users (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   STRING  NOT NULL,
    status BOOLEAN NOT NULL,
    id_tg  INTEGER NOT NULL 
    UNIQUE,
    username STRING,
    language STRING,
    surname STRING);"""

    maps = """CREATE TABLE IF NOT EXISTS maps ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name STRING, 
    flag STRING, 
    http STRING);"""

    # Создание отсутствующих и необходимых таблиц
    con.cursor().execute(users)
    con.cursor().execute(maps)
    con.cursor().execute(question_answer)
    con.commit()


def add_user(user):
    """Создаёт нового пользователя"""
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''INSERT INTO users(name, status, id_tg, username, language, surname)
                            VALUES('{user.first_name}', False, {user.id}, "{user.username}",
                            '{user.language_code}', '{user.last_name}')''')
    con.commit()


def get_answer(key_words):
    con = sqlite3.connect('database.db', check_same_thread=False)
    return con.cursor().execute(f'''SELECT answer FROM question_answer WHERE {key_words.capitalize()}''').fetchone()


def add_que_ans(question, answer):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''INSERT INTO question_answer(key_words, answer)
             VALUES ({question}, {answer})''')
    con.commit()


def get_name_maps(name):
    con = sqlite3.connect('database.db', check_same_thread=False)
    id_category = get_id_category_of_name(name)
    return con.cursor().execute(f'''SELECT id, name, http
             FROM maps WHERE category = "{id_category}"''').fetchall()


def get_id_maps(id_category):
    con = sqlite3.connect('database.db', check_same_thread=False)
    return con.cursor().execute(f'''SELECT id, name, description, http
          FROM maps WHERE category = "{id_category}"''').fetchall()


def add_maps(name, flag, http):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''INSERT INTO maps(name, flag, http)
                         VALUES('{name}', '{flag}', '{http}')''')
    con.commit()


def del_maps(name):
    con = sqlite3.connect('database.db', check_same_thread=False)
    if not is_category(name):
        return False
    con.cursor().execute(f'''DELETE from category WHERE name = "{name}"''')
    con.commit()
    return True


def is_maps(name):
    con = sqlite3.connect('database.db', check_same_thread=False)
    return len(con.cursor().execute(f'''SELECT * FROM maps WHERE name="{name}"''').fetchall()) != 0


def is_status(id_tg):
    con = sqlite3.connect('database.db', check_same_thread=False)
    return len(con.cursor().execute(f'''SELECT * FROM users WHERE id_tg="{id_tg}" and status = True''').fetchall()) != 0


def del_que_ans(question):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''DELETE from question_answer WHERE key_words = "{question}"''')
    con.commit()


def remove_answer(question, answer):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''UPDATE question_answer
            SET answer = '{answer}' WHERE key_words = "{question}"''')
    con.commit()


def remove_status(id_tg):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''UPDATE users
                    SET status = True WHERE id_tg = "{id_tg}"''')
    con.commit()


def get_maps():
    """Возвращает список всех карт"""
    con = sqlite3.connect('database.db', check_same_thread=False)
    return con.cursor().execute('''SELECT * FROM maps''').fetchall()


def get_name_maps():
    """Возвращает список всех карт"""
    con = sqlite3.connect('database.db', check_same_thread=False)
    return con.cursor().execute('''SELECT name FROM maps''').fetchall()


def get_info_for_base():
    """Возвращает базу данных в xlsx таблице"""
    con = sqlite3.connect('database.db', check_same_thread=False)
    itog = []

    users = 'Пользователи', [('ID', 'Имя', 'Должность(1-админ, 0-клиент', 'ID TG', 'UserName', 'Язык', 'Фамилия')] + \
        con.cursor().execute(f'''SELECT id, name, status, id_tg, username, language, surname FROM users''').fetchall()
    itog.append(users)

    maps = 'Карты', [('ID', 'Приватность(Приватная - True, общая - False)', 'Ссылка')] + \
        con.cursor().execute(f'''SELECT id, name, flag, http FROM maps''').fetchall()
    itog.append(maps)

    questions = 'Вопросы', [('Вопрос', 'Ответ')] + \
        con.cursor().execute(f'''SELECT key_words, answer FROM question_answer''').fetchall()
    itog.append(questions)

    workbook = xlsxwriter.Workbook('bot_LUI_БД.xlsx')
    for sheet in itog:
        name, stroki = sheet
        worksheet = workbook.add_worksheet(name)
        for row, stroka in enumerate(stroki):
            for i in range(len(stroka)):
                worksheet.write(row, i, stroka[i])
    workbook.close()
    return


def dow_remove_for_tg(format):
    if format:
        del_all()
    df = pd.read_excel(io='bot_LUI_БД.xlsx', sheet_name=0)
    book = df.head(10000).values
    for lis in book:
        add_user(int(lis[3]), lis[1], lis[4])
        if lis[2]:
            remove_status(int(lis[3]))
    # df = pd.read_excel(io='dow.xlsx', sheet_name=1)
    # book = df.head(10000).values
    # for lis in book:
    #     add_category(lis[1], lis[2])
    # df = pd.read_excel(io='dow.xlsx', sheet_name=2)
    # book = df.head(10000).values
    # for lis in book:
    #     add_notification(lis[0], lis[1])
    # book = df.head(10000).values
    # for lis in book:
    #     add_que_ans(lis[0], lis[1])
    # book = df.head(10000).values
    # for lis in book:
    #     add_discount(lis[0], lis[1])
    print(book)


def del_all():
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''DELETE from maps''')
    con.cursor().execute(f'''DELETE from users''')
    con.cursor().execute(f'''DELETE from question_answer''')
    con.commit()


def get_no_admin_id():
    con = sqlite3.connect('database.db', check_same_thread=False)
    return con.cursor().execute(f'''SELECT id_tg FROM users WHERE status = False''')


# get_info_for_base()
dow_remove_for_tg('bot_LUI_БД.xlsx')
# createBD()
# add_que_ans('12', '34')
# add_maps('new', '1', 'dsajhxa')
# print(get_maps())
# print(con.get_category_assort(0))
# add_category('name', 'ooo')
# del_category('Мужское')
# print(con.is_category('12'))
# print(con.is_assort('12'))
# con.del_assort('12')
# con.del_que_ans('12')
# con.remove_answer('12', '78')
# con.add_user('1233')
# con.remove_status('12')
# add_discount('12', '23')
# print(con.get_discount())
# con.remove_discount('12', '56')
# con.del_discount('12')
# add_notification('12', '122')
# add_assort('789', '98', '00', 1)
# print(con.get_notification())
# con.remove_notification('12', '98')
# con.del_notification('12')
# print(get_info_for_base())
# print(is_status(89))
# dow_remove_for_tg(0)
# add_category('Продукция с Aloe Vera', '1')