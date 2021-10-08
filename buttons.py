from aiogram import types


def process_name_back():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Back')
    return markup


def process_age():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Male", "Female")
    markup.add("Other")
    markup.add('Back')
    return markup


def menu_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu = types.KeyboardButton('About')
    settings_change = types.KeyboardButton('Settings')
    exit_to_menu = types.KeyboardButton('Exit')
    markup.add(menu, settings_change, exit_to_menu)
    return markup


def exit_menu():
    markup = types.ReplyKeyboardRemove(selective=False)
    return markup


def settings():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    change_name = types.KeyboardButton('Change name')
    change_age = types.KeyboardButton('Change age')
    change_gender = types.KeyboardButton('Change sex')
    back_to_menu = types.KeyboardButton('Back')
    markup.add(change_name, change_age, change_gender, back_to_menu)
    return markup


def back_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Back to menu')
    return markup


def gender_back_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Male', 'Female', 'Other', 'Back to menu')
    return markup
