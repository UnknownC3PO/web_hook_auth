import os
import json
import logging
import string

if not os.path.isfile('users_db.json'):
    with open('users_db.json', 'w') as db:
        json.dump({'users': []}, db)


def check_value(message):
    symbols = list(string.punctuation)
    if message.isalpha() and 2 <= len(message) <= 20 and (message.lower() not in ('male', 'female', 'other')):
        if any(i not in symbols for i in message):
            return True
    return False


def reg_user(reg_id, message):
    try:
        with open('users_db.json', 'r+') as reg_db:
            users_data = json.load(reg_db)
            for user in users_data['users']:
                if user['id'] == reg_id:
                    if check_value(message):
                        user['name'] = message
                    elif message.isdigit() and 1 <= int(message) <= 150:
                        user['age'] = message
                    elif message.lower() in ('male', 'female', 'other'):
                        user['sex'] = message
                    else:
                        return False
                    reg_db.seek(0)
                    json.dump(users_data, reg_db)
                    reg_db.truncate()
                    return True
            users_data['users'].append({'id': int(reg_id)})
            reg_db.seek(0)
            json.dump(users_data, reg_db)
            reg_db.truncate()
    except AttributeError:
        logging.exception('RegError')


def change_data(change_id, new_change, value_change):
    try:
        with open('users_db.json', 'r+') as db_change:
            users_data = json.load(db_change)
            for user in users_data['users']:
                if user['id'] == change_id:
                    if check_value(new_change) and value_change == 'Change:change_name':
                        user['name'] = new_change
                    elif new_change.isdigit() and 1 <= int(new_change) <= 150 and value_change == 'Change:change_age':
                        user['age'] = new_change
                    elif new_change.lower() in ('female', 'male', 'other') and value_change == 'Change:change_gender':
                        user['sex'] = new_change
                    else:
                        return False
                db_change.seek(0)
                json.dump(users_data, db_change)
                db_change.truncate()
                return True
    except NameError:
        logging.exception('Error')


def about_user(about_id):
    with open('users_db.json', 'r+') as about:
        users_data = json.load(about)
        for user in users_data['users']:
            if user['id'] == about_id:
                return 'Name:{}\nAge:{}\nGender:{}'.format(user['name'], user['age'], user['sex'])
