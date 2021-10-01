import os
import json
import logging

if not os.path.isfile('users_db.json'):
    with open('users_db.json', 'w') as db:
        json.dump({'users': []}, db)



def reg_user(reg_id, message):
    try:
        with open('users_db.json', 'r+') as reg_db:
            users_data = json.load(reg_db)
            for user in users_data['users']:
                if user['id'] == reg_id:
                    if message.isalpha() and 2 <= len(message) <= 20 and message.lower() not in ('male', 'female','other'):
                        user['name'] = message
                    elif message.isdigit():
                        user['age'] = message
                    elif message.lower() in ('male', 'female','other'):
                        user['sex'] = message
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


def change_data(change_id, new_change):
    try:
        with open('users_db.json', 'r+') as db_change:
            users_data = json.load(db_change)
            for user in users_data['users']:
                if user['id'] == change_id:
                    if new_change[0:12] == '/name_update':
                        user['name'] = new_change[13:]
                    elif new_change[0:11] == '/age_update':
                        user['age'] = new_change[12:]
                    elif new_change[0:11] == '/sex_update':
                        user['sex'] = new_change[12:]
                db_change.seek(0)
                json.dump(users_data, db_change)
                db_change.truncate()
                return True
    except NameError:
        logging.exception('Error')
