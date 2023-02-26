import os
from datetime import datetime

import openpyxl

from auxiliary.req_data import *


# функция для улучшения читабельности кода и удобства (вызывает другие функции)
def all_cycle(filename, ender):
    file_delete()
    file_renamer(filename, ender)


# удаляет временные xlsx, csv файлы
def file_delete():
    try:
        os.remove(src_current_schedule)
    except Exception:
        pass


def file_renamer(filename, ender):
    os.rename(
        f"{src_files}{filename}.{ender}",
        f"{src_files}current_schedule.xlsx"
    )


# TODO automatically date update in schedule_template.xlsx function

# функция обработчик для получения расписания
async def get_schedule(doctor, time_period):
    wb_obj = openpyxl.load_workbook(src_current_schedule)  # обработка файла
    sheet_obj = wb_obj[doctor]  # выбор листа для работы (по фио)

    max_row = sheet_obj.max_row  # максимальное количество строк

    if time_period == 'today':
        result = await get_today_schedule(sheet_obj, max_row)
    else:
        result = await get_weekly_schedule(sheet_obj, max_row)

    return result


# функция для получения расписания только на сегодня
async def get_today_schedule(sheet_obj, max_row):
    max_column = sheet_obj.max_column  # максимальное количество столбцов

    today = datetime.now().strftime("%d-%m-%Y")
    cords = None
    for i in range(1, max_column + 1):
        cell = sheet_obj.cell(row=2, column=i).value
        try:
            if cell.strftime("%d-%m-%Y") == today:
                cords = i
        except Exception:
            continue

    result = []
    if cords is None:
        result = 'На сегодня нет расписания'
    else:
        for i in range(4, max_row + 1):
            none_counter = 0
            counter = 0
            pre_result = []
            for j in range(cords, cords + 7):
                cell = sheet_obj.cell(row=i, column=j).value
                pre_result.append(cell)
                if cell is None:
                    none_counter += 1
                counter += 1
                if counter == 7:
                    if none_counter != 7:
                        # TODO отрефакторить вывод расписания
                        result.append(pre_result)
                    break

    return result


# функция для получения расписания на неделю
async def get_weekly_schedule(sheet_obj, max_row):
    counter, start, finish = 0, 1, 8
    result = []
    for _ in range(7):
        day_none_counter = 0
        for i in range(1, max_row + 1):
            if i in [1, 2]:
                finish = start + 2
                f1 = 2
            else:
                finish = start + 7
                f1 = 7
            none_counter = 0
            pre_result = []
            for j in range(start, finish):
                cell = sheet_obj.cell(row=i, column=j).value
                pre_result.append(cell)
                if cell is None:
                    none_counter += 1
                counter += 1
                if counter == f1:
                    if none_counter != f1:
                        # TODO отрефакторить вывод расписания
                        result.append(pre_result)
                    else:
                        if none_counter == f1:
                            day_none_counter += 1
                        if day_none_counter == max_row - 3:
                            # TODO отрефакторить вывод расписания
                            result.append('В этот день нет записей')
                    counter = 0
                    break
        start, finish = finish + 1, start + 7

    return result
