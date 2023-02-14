import sqlite3

from loguru import logger

from auxiliary.req_data import *

global connection, cursor


# создание соединения с бд
async def start_connection():
    global connection, cursor

    try:
        connection = sqlite3.connect(src_db)
        cursor = connection.cursor()
    except Exception as ex:
        logger.error(ex)


# удаление соединения с бд
async def close_connection():
    global connection

    try:
        if connection:
            connection.close()
    except Exception as ex:
        logger.error(ex)


# код для создания таблицы. Только нужно добавлять данные о документах в эту же бд, но можно в другую таблицу только с документами (связывать по primary key или id пользователя)
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


# функция для получения данных из бд
# TODO В дальнейшем нужно добавить аргумент для вызова, от которого будет зависеть какая информация будет возвращаться
async def get_data():
    try:
        await start_connection()
        cursor.execute(f"""SELECT * FROM users""")
        # TODO сразу здесь реализовать через fetchall что и откуда мы хотим получить через if/else
        # return *значение*
        await close_connection()
    except Exception as ex:
        logger.error(ex)


# функция для добавления нового пользователя в бд
async def add_new_user(id_tg, first_name, username, post, date_added, date_removed):
    await start_connection()
    cursor.execute(
        'INSERT INTO users (id, first_name, username, post, date_added, date_removed) VALUES (?,?,?,?,?,?);',
        (id_tg, first_name, username, post, date_added, date_removed)
    )
    connection.commit()
    logger.info(f'Added new user to table users | {id_tg}, {first_name}, {username}, {post}')
    await close_connection()


# функция для удаления пользователя из бд
async def remove_user(id_tg):
    await start_connection()
    cursor.execute(
        f"""DELETE FROM users WHERE id = '{id_tg}'""",
    )
    connection.commit()
    logger.info(f'Delete user from table users | {id_tg}')
    await close_connection()

# TODO реализовать функцию перевода из Excel файла в sql таблицу (schedule созданную отдельно, один раз)
#  при помощи обновления таблицы созданную только для расписания (связать с таблицей users при помощи primary key или id пользователя)
