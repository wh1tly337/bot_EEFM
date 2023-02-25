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


# код для создания таблицы. Только нужно добавлять данные о документах
# в эту же бд, но можно в другую таблицу только с документами
# (связывать по primary key или id пользователя)
# async def make_table():
#     await start_connection()
#     cursor.execute(f"""CREATE TABLE users
#  (
#     id           SERIAL PRIMARY KEY,
#     id_tg        INTEGER,
#     first_name   VARCHAR(255),
#     username     VARCHAR(255),
#     post         VARCHAR(13),
#     date_added   DATE,
#     date_removed DATE
#  );""")
#     await close_connection()

async def get_all_ids():
    try:
        await start_connection()
        # cursor.execute(f"""SELECT * FROM users""")
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
    """ Функция поиска данных """
    # field - столбец в бд, по которому поиск
    # what_need - если что-то конкретное надо вывести (необязательный)
    # value - то, чему равен столбец в бд
    try:
        await start_connection()
        # cursor.execute(f"""SELECT * FROM users""")
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


async def add_new_document(id, date_start, date_finish):
    try:
        await start_connection()
        cursor.execute(
            'INSERT INTO documents'
            '(user_id, date_start, date_finish)'
            'VALUES (?, ?, ?)',
            (id, date_start, date_finish)
        )
        connection.commit()
        logger.info(f'Added new user to table users | '
                    f'{id}, '
                    f'{date_start}, '
                    f'{date_finish}')
        await close_connection()
    except Exception as ex:
        logger.error(ex)


# TODO async def update_user():
async def update_user(field, current, needed):
    try:
        await start_connection()
        cursor.execute(f"""UPDATE users SET {field} = '{needed}' 
        WHERE {field} = '{current}'""")
        connection.commit()
        await close_connection()
    except Exception as ex:
        logger.error(ex)


async def remove_user(id_tg):
    """ Функция удаления пользователя из бд"""
    try:
        await start_connection()
        cursor.execute(f"""DELETE FROM users WHERE id = '{int(id_tg)}'""")
        connection.commit()
        logger.info(f'Delete user from table users | {id_tg}')
        await close_connection()
    except Exception as ex:
        logger.error(ex)


# TODO реализовать функцию чтобы директор вручную мог добавлять врачей

async def add_user_manual():
    ...


# функция для копирования информации из .csv файла в таблицу бд schedule
async def add_schedule(filename):
    await start_connection()
    cursor.execute(
        f"""COPY schedule 
        FROM '{src_files}{filename}.csv' DELIMITER ';' CSV HEADER;""")
    connection.commit()
    await close_connection()
