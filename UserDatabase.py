import json
import os
from typing import Any

import User
from telegram import Update

def user_reader(): #Reads the user list from the JSON-file!
    user_list = []

    if os.path.isfile("users.json") and os.path.getsize("users.json") > 0:
        try:
            with open("users.json", "r") as f:
                data = json.load(f)

            for user_data in data:
                user_object = User.User(user_data['id'], user_data['nick'], user_data['tags'], user_data['user_type'], user_data['user_lang'])
                user_list.append(user_object)

        except FileNotFoundError:
            print("File not found!")
        except json.JSONDecodeError:
            print("Invalid JSON data in the file!")

    return user_list




def user_writer(user_list): #Writes user data back to the users.json -file

    try:
        with open("Users.json", "w") as f:
            json.dump(user_list, f, cls=User.CustomerEncoder)
            print("User added to the users.json")


    except FileNotFoundError:
        print("Something went wrong")


def get_user_lang(update: Update) -> str | None:
    current_user_id = update.message.from_user.id
    user_list = user_reader()
    for user in user_list:
        if current_user_id == user.id:
            return user.user_lang

    return


def get_user_type(update: Update) -> int:
    current_user_id = update.message.from_user.id
    user_list = user_reader()
    for user in user_list:
        if current_user_id == user.id:
            return user.user_type
