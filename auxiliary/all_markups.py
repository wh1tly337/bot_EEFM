from aiogram import types

# файл отвечающий за регистрацию/создание кнопок под клавиатурой (вызываются и добавляются в тг из других мест)

markup_new_user = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_new_user = types.KeyboardButton('Получить доступ')
btn2_new_user = types.KeyboardButton('Отмена')
markup_new_user.add(btn1_new_user, btn2_new_user)

markup_test = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_test = types.KeyboardButton('Что-то одно')
btn2_test = types.KeyboardButton('Что-то другое')
markup_test.add(btn1_test, btn2_test)

markup_cancel = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_cancel = types.KeyboardButton('Отмена')
markup_cancel.add(btn1_cancel)
