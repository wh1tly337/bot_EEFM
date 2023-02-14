from aiogram import types

# файл отвечающий за регистрацию/создание кнопок под клавиатурой (вызываются и добавляются в тг из других мест)

markup_new_user = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_new_user = types.KeyboardButton('Получить доступ')
btn2_new_user = types.KeyboardButton('Отмена')
markup_new_user.add(btn1_new_user, btn2_new_user)

markup_doctor = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_doctor = types.KeyboardButton('Получить расписание')
markup_doctor.add(btn1_doctor)

markup_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_admin = types.KeyboardButton('Расписание')
btn2_admin = types.KeyboardButton('Отправить сообщение')
markup_admin.add(btn1_admin, btn2_admin)

markup_admin_schedule = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_admin_schedule = types.KeyboardButton('Получить шаблон')
btn2_admin_schedule = types.KeyboardButton('Загрузить расписание')
btn3_admin_schedule = types.KeyboardButton('Отмена')
markup_admin_schedule.add(btn1_admin_schedule, btn2_admin_schedule)
markup_admin_schedule.add(btn3_admin_schedule)

markup_admin_message = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_admin_message = types.KeyboardButton('Рассылка')
btn2_admin_message = types.KeyboardButton('Директору')
btn3_admin_message = types.KeyboardButton('Отмена')
markup_admin_message.add(btn1_admin_message, btn2_admin_message)
markup_admin_message.add(btn3_admin_message)

markup_director = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_director = types.KeyboardButton('Управление персоналом')
btn2_director = types.KeyboardButton('Получить расписание')
markup_director.add(btn1_director, btn2_director)

markup_cancel = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_cancel = types.KeyboardButton('Отмена')
markup_cancel.add(btn1_cancel)
