import sqlite3

from loguru import logger

from auxiliary.req_data import *

global connection, cursor


async def start_connection():
    """ Создание соединения с бд """
    global connection, cursor

    try:
        connection = sqlite3.connect(src_db)
        cursor = connection.cursor()
    except Exception as ex:
        logger.error(ex)


async def close_connection():
    """ Удаление соединения с бд """
    global connection

    try:
        if connection:
            connection.close()
    except Exception as ex:
        logger.error(ex)


async def get_all_ids():
    """ Функция для получения всех id из бд"""
    try:
        await start_connection()
        cursor.execute(f"""SELECT id FROM users""")
        taken = cursor.fetchall()
        result = []
        for i in range(len(taken)):
            result.append(*taken[i])
        await close_connection()
        return result
    except Exception as ex:
        logger.error(ex)


async def get_id_with_fio(emp_data):
    """ Функция для получения id и фамилии"""
    try:
        await start_connection()
        surname = emp_data[0]
        name = emp_data[1]
        patronymic = emp_data[2]
        cursor.execute(f"""
        SELECT id
        FROM users
        WHERE surname = '{surname}' AND
        name = '{name}' AND
        patronymic = '{patronymic}'
        """)
        return cursor.fetchall()
    except Exception as ex:
        logger.error(ex)


async def get_data(field, value, what_need='all'):
    """ Функция поиска запрашиваемых данных """
    # field - столбец в бд, по которому поиск
    # what_need - если что-то конкретное надо вывести (необязательный)
    # value - то, чему равен столбец в бд
    try:
        await start_connection()
        cursor.execute(f"""SELECT * FROM users WHERE {field} = '{value}'""")
        if what_need == 'id':
            result = cursor.fetchall()[0][0]
        elif what_need == 'post':
            result = cursor.fetchall()[0][5]
        else:
            result = cursor.fetchall()[0]
        await close_connection()
        return result
    except Exception as ex:
        logger.error(ex)


async def get_documents(id):
    """ Функция поиска документов """
    try:
        await start_connection()
        cursor.execute(f"""SELECT date_start, date_finish, name
        FROM documents
        WHERE user_id = {id}""")
        result = cursor.fetchall()
        print(result)
        await close_connection()
        return result
    except Exception as ex:
        logger.error(ex)


async def login_user(tg_id):
    """ Функция регистрирования пользователя """
    # происходит каждый раз после перезапуска бота и написания пользователем 
    # /start (нужно для корректной работы admin_file_handler) (меняет 
    # переменную log_stat в бд)
    try:
        await start_connection()
        cursor.execute(f"""UPDATE users SET log_stat = 1 WHERE id = {tg_id}""")
        connection.commit()
        await close_connection()
    except Exception as ex:
        logger.error(ex)


async def logout_user():
    """ Функция разлогинивания пользователя """
    # происходит каждый перед выключением бота (меняет переменную log_stat в бд)
    try:
        await start_connection()
        cursor.execute(f"""UPDATE users SET log_stat = 0 WHERE log_stat = 1""")
        connection.commit()
        await close_connection()
    except Exception as ex:
        logger.error(ex)


async def add_new_user(
        id_tg,
        surname,
        name,
        patronymic,
        username,
        post,
        date_added=None,
        date_removed=None
):
    """ Функция добавления нового пользователя """
    try:
        await start_connection()
        cursor.execute(
            'INSERT INTO users '
            '(id, surname, name, patronymic, username, post, date_added,'
            ' date_removed)'
            'VALUES (?,?,?,?,?,?,?,?);',
            (id_tg, surname, name, patronymic, username, post, date_added,
             date_removed)
        )
        connection.commit()
        logger.info(f'Added new user to table users | '
                    f'{id_tg}, '
                    f'{surname}, '
                    f'{name}, '
                    f'{patronymic}, '
                    f'{username}, '
                    f'{post}')
        await close_connection()
    except Exception as ex:
        logger.error(ex)


async def add_new_document(id, date_start, date_finish, name):
    """ Функция добавления документа """
    try:
        await start_connection()
        cursor.execute(
            'INSERT INTO documents'
            '(user_id, date_start, date_finish, name)'
            'VALUES (?, ?, ?, ?)',
            (id, date_start, date_finish, name)
        )
        connection.commit()
        logger.info(f'Added new document to table documents | '
                    f'{id}, '
                    f'{date_start}, '
                    f'{date_finish}')
        await close_connection()
    except Exception as ex:
        logger.error(ex)


# TODO если у сотрудников одинаковая фамилия\имя, то он поменяет для обоих
# TODO Саша хотел ее переписать !!!
# TODO Саша поменяй в своих функциях переменную id на что-то другое
async def update_user(field, current, needed):
    try:
        await start_connection()
        cursor.execute(f"""UPDATE users SET {field} = '{needed}' 
        WHERE {field} = '{current}'""")
        connection.commit()
        await close_connection()
    except Exception as ex:
        logger.error(ex)


# TODO Саша пропиши комментарии для твоих функций (что они делают)
async def update_with_id_user(field, id, needed):
    try:
        id = id[0][0]
        await start_connection()
        cursor.execute(f"""UPDATE users SET {field} = '{needed}'
        WHERE id = '{id}'""")
        connection.commit()
        await close_connection()
    except Exception as ex:
        logger.error(ex)


async def remove_user(id_tg):
    """ Функция удаления пользователя из бд"""
    try:
        await start_connection()
        cursor.execute(f"""DELETE FROM users WHERE id = '{id_tg}'""")
        connection.commit()
        logger.info(f'Delete user from table users | {id_tg}')
        await close_connection()
    except Exception as ex:
        logger.error(ex)
