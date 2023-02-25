import os
from datetime import datetime

import openpyxl
import pandas as pd

from auxiliary.req_data import *


# функция для улучшения читабельности кода и удобства (вызывает другие функции)
def all_cycle(filename, ender):
    xlsx_to_csv(filename, ender)
    get_some_info()
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

# Шешенин Владимир Киприянович
# Газимов Игорь Грегорьевич
def get_some_info(doctor='Газимов Игорь Грегорьевич', time_period='week'):
    wb_obj = openpyxl.load_workbook(src_schedule_template)  # обработка файла
    sheet_obj = wb_obj[doctor]  # выбор листа для работы (по фамилии)

    max_row = sheet_obj.max_row  # максимальное количество строк
    max_column = sheet_obj.max_column  # максимальное количество строк

    if time_period == 'today':
        today = datetime.now().strftime("%d-%m-%Y")
        cords = None
        for i in range(1, max_column + 1):
            cell = sheet_obj.cell(row=2, column=i).value
            try:
                if cell.strftime("%d-%m-%Y") == today:
                    cords = i
            except Exception:
                continue

        if cords is None:
            print("Нет такой даты")
        else:
            for i in range(4, max_row + 1):
                none_counter = 0
                counter = 0
                result = []
                for j in range(cords, cords + 7):
                    cell = sheet_obj.cell(row=i, column=j).value
                    result.append(cell)
                    if cell is None:
                        none_counter += 1
                    counter += 1
                    if counter == 7:
                        if none_counter != 7:
                            print(result)
                        break
    else:
        counter, start, finish = 0, 1, 8
        for _ in range(7):
            for i in range(2, max_row + 1):
                none_counter = 0
                result = []
                for j in range(start, finish):
                    cell = sheet_obj.cell(row=i, column=j).value
                    result.append(cell)
                    if cell is None:
                        none_counter += 1
                    counter += 1
                    if counter == 7:
                        if none_counter != 7:
                            print(result)
                        else:
                            print("Нет записей")
                        break
            start, finish = finish + 1, start + 7
