import os

import openpyxl
import pandas as pd

from auxiliary.req_data import *


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
    get_some_info()
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

def get_some_info():
    wb_obj = openpyxl.load_workbook(src_schedule_template)  # обработка файла
    # TODO лист нужно будет вызвать с функцией (по фамилии)
    sheet_obj = wb_obj.active  # выбор листа для работы

    row = sheet_obj.max_row  # максимальное количество строк
    column = sheet_obj.max_column  # максимальное количество столбцов

    counter, start, finish = 0, 1, 8
    s1, s2 = 1, 2
    # TODO поменять этот алгоритм, потому что это какой-то некрасивый пиздец
    for _ in range(7):  # этот цикл проходит по 7 дням в неделе
        day_none_counter = 0
        # 1 = с заголовками, датой, днем неделей
        # 4 = просто записи
        for i in range(1, row + 1):  # цикл проходящий по всем строкам
            if i == s1 or i == s2:
                finish = start + 2
                f1 = 2
            else:
                finish = start + 7
                f1 = 7

            none_counter = 0
            result = []
            for j in range(start, finish):  # цикл проходящий по столбцам
                # от start до finish
                cell_obj = sheet_obj.cell(row=i, column=j)

                if cell_obj.value is None:
                    none_counter += 1

                result.append(cell_obj.value)

                counter += 1
                if counter == f1:
                    if none_counter == f1:
                        day_none_counter += 1
                    else:
                        print(*result)
                        print("")

                    counter = 0
                    break

        if day_none_counter == row - 3:
            print('Сегодня нет записей')

        start, finish = finish + 1, start + 7
        print("")
        print("")
