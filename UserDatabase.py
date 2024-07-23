import json
import os
import Filepaths

import User
from telegram import Update
from typing import List


def user_reader(): #Reads the user list from the JSON-file! #better name would be get_user_list
    user_list = []

    if os.path.isfile(Filepaths.users_file) and os.path.getsize(Filepaths.users_file) > 0:
        try:
            with open(Filepaths.users_file, "r") as f:
                data = json.load(f)

            for user_data in data:
                user_object = User.User(user_data['id'], user_data['nick'], user_data['tags'], user_data['user_type'],
                                        user_data['user_lang'])
                user_list.append(user_object)

        except FileNotFoundError:
            print("File not found!")
        except json.JSONDecodeError:
            print("Invalid JSON data in the file!")

    else:
        print("Something weird happened!")

    return user_list




def user_writer(user_list): #Writes user data back to the users.json -file

    try:
        with open(Filepaths.users_file, "w") as f:
            json.dump(user_list, f, cls=User.CustomerEncoder)
            print(f"User added to the {Filepaths.users_file}")


    except FileNotFoundError:
        print("Something went wrong")


def get_user_lang(update: Update):
    try:
        current_user_id = update.message.from_user.id
    except AttributeError:
        try:
            current_user_id = update.callback_query.from_user.id
        except AttributeError:
            return

    user_list = user_reader()
    for user in user_list:
        if current_user_id == user.id:
            return user.user_lang

    return

def get_user_lang_code(update: Update) -> int:
    user_lang = get_user_lang(update)
    if user_lang == "fi":
        return 0
    else:
        return 1


def get_user_type(update: Update) -> int:
    current_user_id = update.message.from_user.id
    user_list = user_reader()
    for user in user_list:
        if current_user_id == user.id:
            return user.user_type


def get_admins():
    user_list = user_reader()
    admin_list = []
    for user in user_list:
        if user.user_type >= 3:
            admin_list.append(user)
    return admin_list

def get_user_id(user_name):
    user_list = user_reader()
    for user in user_list:
        if user.nick == user_name:
            return user.id

    return "no user found"

def delete_user(user_id):
    user_list = user_reader()
    for user in user_list:
        if user.id == user_id:
            user_list.remove(user)
    user_writer(user_list)

def get_current_user(update: Update):
    user_list = user_reader()
    current_user_id = update.message.from_user.id
    for user in user_list:
        if user.id == current_user_id:
            return user

    return False


def get_user_by_username(username):
    user_list = user_reader()
    for user in user_list:
        if user.nick == username:
            return user
    return

def get_user_info_text(update: Update):
    user = get_current_user(update)
    output_text = f"This is your current information:\n\nUser id:\t\t{user.id}\nNickname:\t\t{user.nick}\nCurrent tags:\t\t{user.tags}\n" \
                  f"Languange:\t\t{user.user_lang}\nAccount type:\t\t{user.user_type}"
    return output_text

def is_user(update):
    user_id = update.message.from_user.id
    user_list = user_reader()
    user_found = False
    user_nick_not_found = False

    for user in user_list:
        if user.id == user_id:
            if user.nick == None:
                user.nick = update.message.from_user.username
                user_nick_not_found = True
            user_found = True

    if user_nick_not_found:
        user_writer(user_list)
        print("User nick updated")


    print(f"user found: {user_found}")

    return user_found

def update_username(update: Update):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username
    user_list = user_reader()
    for user in user_list:
        if user.id == user_id:
            if user.nick != user_name:
                user.nick = user_name

    user_writer(user_list)
    return

def update_tags(tag_list, user_id):
    user_list = user_reader()
    for user in user_list:
        if user.id == user_id:
            user.tags = tag_list

    user_writer(user_list)
    return