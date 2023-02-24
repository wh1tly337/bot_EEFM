from aiogram import types

# файл отвечающий за регистрацию/создание кнопок под клавиатурой
# (вызываются и добавляются в тг из других мест)
''' Кнопка старта для бота (не обязательная) '''
markup_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn_start = types.KeyboardButton('/start')
markup_start.add(btn_start)

''' Кнопка отмены для всех пользователей '''
markup_cancel = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn_cancel = types.KeyboardButton('Отмена')
markup_cancel.add(btn_cancel)

''' Кнопки ДА/НЕТ '''
markup_yes_no = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn_yes = types.KeyboardButton('Да')
btn_no = types.KeyboardButton('Нет')
markup_yes_no.add(btn_yes, btn_no)

''' Кнопки для нового пользователя '''
markup_new_user = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_new_user = types.KeyboardButton('Получить доступ')
markup_new_user.add(btn1_new_user)

''' Кнопки 1-го уровня для доктора '''
markup_doctor = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_doctor = types.KeyboardButton('Получить расписание')
markup_doctor.add(btn1_doctor)

''' Кнопки 1-го уровня для админа '''
markup_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_admin = types.KeyboardButton('Расписание')
btn2_admin = types.KeyboardButton('Отправить сообщение')
markup_admin.add(btn1_admin, btn2_admin)

''' Кнопки 2-го уровня (расписания) для админа '''
markup_admin_make_schedule = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_admin_make_schedule = types.KeyboardButton('Получить шаблон')
btn2_admin_make_schedule = types.KeyboardButton('Загрузить расписание')
btn3_admin_make_schedule = types.KeyboardButton('Посмотреть расписание')
markup_admin_make_schedule.add(btn1_admin_make_schedule,
                               btn2_admin_make_schedule)
markup_admin_make_schedule.add(btn3_admin_make_schedule)
markup_admin_make_schedule.add(btn_cancel)

''' Кнопки 2-го уровня (сообщения) для админа '''
markup_admin_message = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_admin_message = types.KeyboardButton('Рассылка')
btn2_admin_message = types.KeyboardButton('Директору')
markup_admin_message.add(btn1_admin_message, btn2_admin_message)
markup_admin_message.add(btn_cancel)

''' Кнопки 3-го уровня (расписания) для админа '''
markup_admin_watch_schedule = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_admin_watch_schedule = types.KeyboardButton('На сегодня')
btn2_admin_watch_schedule = types.KeyboardButton('На неделю')
markup_admin_watch_schedule.add(btn1_admin_watch_schedule,
                                btn2_admin_watch_schedule)
markup_admin_watch_schedule.add(btn_cancel)

''' Кнопки 1-го уровня для директора '''
markup_director = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_director = types.KeyboardButton('Управление персоналом')
btn2_director = types.KeyboardButton('Получить расписание')
markup_director.add(btn1_director, btn2_director)

''' Кнопки 2-го уровня для директора '''
markup_director_emp = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_director_emp = types.KeyboardButton('Найти сотрудника')
btn2_director_emp = types.KeyboardButton('Добавить сотрудника ')
btn3_director_emp = types.KeyboardButton('Удалить сотрудника')
btn4_director_emp = types.KeyboardButton('Передать права директора')
markup_director_emp.add(btn1_director_emp)
markup_director_emp.add(btn2_director_emp, btn3_director_emp)
markup_director_emp.add(btn4_director_emp)
