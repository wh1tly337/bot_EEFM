import os

import pandas as pd

from auxiliary.req_data import *
from workers import db_worker as dbw


# import openpyxl as op


# TODO xlsx to csv/db and handle info function.
#  Нужно добавлять из excel таблицы информацию в отдельную таблицу бд, чтобы
#  там хранилась информация о целом месяце, потом старая информация будет
#  удалятся. Программа будет считывать дату из excel и вставлять информацию по
#  этой дате в бд (ключевое поле дата), те администратор заполняет расписание
#  на неделю, а в таблице бд информация хранится за прошлую, текущую и
#  следующую неделю

# функция для улучшения читабельности кода и удобства (вызывает другие функции)
def all_cycle(filename, ender):
    xlsx_to_csv(filename, ender)
    # dbw.add_schedule(filename)
    file_delete(filename, ender)


# конвертирует xlsx файлы в csv
def xlsx_to_csv(filename, ender):
    converter = pd.read_excel(f"{src_files}{filename}.{ender}")
    converter.to_csv(
        f"{src_files}{filename}.csv",
        index=False,
        header=True,
        sep=";"
    )


# удаляет временные xlsx, csv файлы
def file_delete(filename, ender):
    os.remove(f"{src_files}{filename}.{ender}")
    os.remove(f"{src_files}{filename}.csv")

# TODO automatically date update in schedule_template.xlsx function

# TODO add watch schedule on today and on week function
