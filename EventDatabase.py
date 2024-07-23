# This file handles all the handling of the event lists like writing them to events.json file.
# Event creation itself is handled in EventSaver.py


# only_upcoming returns only the upcoming events
# events_reader reads the events.json
# get_unaccepted_events returns events, that have accepted tag as False
# get_accepted_events return events, that have accepted tag as True
# event_parser_normal returns an event text ready to be send to user
# event_parser_all returns an event text with all possible fields.
# This is used for organizers and admins to check that all event fields are okay
# event_backup_load loads the list of events backed up
# event_backup_save saves the event to events_backup.json -file
# event_finder_by_creator returns an event made by certain user

import json
from telegram.ext import ContextTypes
from telegram import Update
from typing import List
from datetime import datetime

import Event
import logging

import EventSaver
import Filepaths

import UserDatabase

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_only_upcoming():
    event_list = events_reader(Filepaths.events_file)
    event_list_only_upcoming = []
    for event in event_list:
        if event.start_time.date() >= datetime.now().date() and event.end_time == None:
            event_list_only_upcoming.append(event)
        else:
            if event.start_time.date() >= datetime.now().date() and event.end_time > datetime.now():
                event_list_only_upcoming.append(event)

    return event_list_only_upcoming


def events_reader(file_name: str):
    event_list = []

    try:

        with open(file_name, "r") as file:
            content = file.read()

        modified_content = content.replace("}]", "},\n]")
        data = json.loads(modified_content)

        for event_data in data:
            start_time_str = event_data['start_time']
            end_time_str = event_data['end_time']
            sell_time_str = event_data['ticket_sell_time']

            # Gets the start and end times and turns them into datetime objects
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S") if start_time_str else None
            end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S") if end_time_str else None
            ticket_sell_time = datetime.strptime(sell_time_str, "%Y-%m-%d %H:%M:%S") if sell_time_str else None

            event_object = Event.Event(
                event_data['id'],
                event_data['creator'],
            )
            event_object.name = event_data['name']
            event_object.start_time = start_time
            event_object.end_time = end_time
            event_object.ticket_sell_time = ticket_sell_time
            event_object.location = event_data['location']
            event_object.description_fi = event_data['description_fi']
            event_object.description_en = event_data['description_en']
            event_object.ticket_link = event_data['ticket_link']
            event_object.other_link = event_data['other_link']
            event_object.accessibility_fi = event_data['accessibility_fi']
            event_object.accessibility_en = event_data['accessibility_en']
            event_object.price = event_data['price']
            event_object.dc = event_data['dc']
            event_object.accepted = event_data['accepted']
            try:
                event_object.tags = event_data['tags']
            except KeyError:
                event_object.tags = ["all"]
            try:
                event_object.stage = event_data["stage"]
            except:
                event_object.stage = 99

            event_list.append(event_object)

    except FileNotFoundError:
        print("File not found!")
        try:
            with open(file_name, "w") as f:
                print("File created!")

        except:
            print("Something went wrong!")


    except json.JSONDecodeError:
        print("Invalid JSON data in the file!")

    except Exception:
        print("Something went wrong with the event reading from jsons")

    return event_list


def events_writer(event_list):
    try:
        with open(Filepaths.events_file, "w") as f:
            json.dump(event_list, f, cls=Event.EventEncoder, indent=4, separators=(',', ': '))
            print("Event saved")


    except FileNotFoundError:
        print("Something went wrong")


def get_event_by_id(id: int, file_name):
    event_list = events_reader(file_name)
    for event in event_list:
        if int(event.id) == id:
            return event

    return None


def get_unaccepted_events():
    event_list = events_reader(Filepaths.events_backup_file)
    unaccepted_events = []
    for event in event_list:
        if event.stage == EventSaver.STAGE_SUBMITTED:
            unaccepted_events.append(event)

    return unaccepted_events


def get_accepted_events():
    event_list = get_only_upcoming()
    accepted_events = []
    for event in event_list:
        if event.accepted:
            accepted_events.append(event)

    return accepted_events



def get_events_by_tag(tag):
    events = get_accepted_events()
    event_list = []
    for event in events:
        if tag in event.tags:
            event_list.append(event)

    return event_list


def delete_event(event_id):
    event_list = events_reader(Filepaths.events_file)
    updated_event_list = []

    for event in event_list:
        if event_id != event.id:
            updated_event_list.append(event)

    events_writer(updated_event_list)

    return

def save_changes_to_accepted_event(event_to_be_saved):

    event_list = events_reader(Filepaths.events_file)

    event_list_to_be_saved = []

    for event in event_list:
        if event.id == event_to_be_saved.id:
            event_list_to_be_saved.append(event_to_be_saved)
        else:
            event_list_to_be_saved.append(event)
    
    events_writer(event_list_to_be_saved)

    return



def get_head(event, user_lang_code) -> str:
    prompts = [["Klo: ", "-", "Alkaa", "klo", "Päättyy", "klo", "klo: ", "Hinta: ", "Liput", "Lipunmyyntipäivä"],
               ["from", "to", "Starts", "at", "Ends", "at", "at", "Price", "Tickets: ", "Ticket sale time"]]

    tag_string = ""
    
    for tag in event.tags:
        try:
            en_tag, fi_tag = tag.split("//")
        except ValueError:
            en_tag = tag
            fi_tag = tag
        if user_lang_code == 0:
            tag_string += f"#{fi_tag.strip()} "
        else:
            tag_string += f"#{en_tag.strip()} "

    tag_string = f"{tag_string}\n\n"
    

    if "//" in event.name:
        event_name_fi, event_name_eng = event.name.split("//", 1)
        event_name_fi = event_name_fi.strip()
        event_name_eng = event_name_eng.strip()
    else:
        event_name_fi = event.name
        event_name_eng = event.name

    event_name = [event_name_fi, event_name_eng]

    text_head = ""
    start_time_full = event.start_time

    start_date = start_time_full.strftime("%d.%m.%Y")
    start_time = start_time_full.strftime("%H:%M")

    try:
        end_time_full = event.end_time
        end_date = end_time_full.strftime("%d.%m.%Y")
        end_time = end_time_full.strftime("%H:%M")

        if start_date == end_date:
            text_head = (
                f"{tag_string}*{event_name[user_lang_code].upper()}* - {start_date}\n"
                f"{prompts[user_lang_code][0]} {start_time} {prompts[user_lang_code][1]} {end_time}\n")

        if end_date != start_date:
            text_head = (f"{tag_string}*{event_name[user_lang_code].upper()}*\n" \
                         f"{prompts[user_lang_code][2]}\t{start_date} {prompts[user_lang_code][3]} {start_time}\n"
                         f"{prompts[user_lang_code][4]}\t{end_date} {prompts[user_lang_code][5]} {end_time}\n\n")


    except AttributeError:
        text_head = (
            f"{tag_string}*{event_name[user_lang_code].upper()}*\n"
            f"{start_date} {prompts[user_lang_code][6]} {start_time}->\n")

    return text_head


def get_body(event, user_lang_code):
    prompts = [["Klo: ", "-", "Alkaa", "klo", "Päättyy", "klo", "klo: ", "Hinta: ", "Liput:", "Lipunmyyntipäivä", "Lisää tietoja:"],
        ["from", "to", "Starts", "at", "Ends", "at", "at", "Price", "Tickets:", "Ticket sale time", "More info at:"]]


    # dc
    if "//" in event.dc:
        event_dc_fi, event_dc_en = event.dc.split("//", 1)
        event_dc_fi = event_dc_fi.strip()
        event_dc_en = event_dc_en.strip()
    else:
        event_dc_fi = event.dc
        event_dc_en = event.dc

    # location
    if "//" in event.location:
        event_location_fi, event_location_en = event.location.split("//", 1)
        event_location_fi = event_location_fi.strip()
        event_location_en = event_location_en.strip()
    else:
        event_location_fi = event.location
        event_location_en = event.location

    # make the body
    if user_lang_code == 0:
        text_body = (f"\nTapahtumapaikka: {event_location_fi}\nDresscode: {event_dc_fi}\n\n")

    else:
        text_body = (f"\nLocation: {event_location_en}\nDresscode: {event_dc_en}\n\n")

    # ticket sell time and info
    try:
        ticket_sell_time_full = event.ticket_sell_time
        ticket_sell_time = ticket_sell_time_full.strftime("%d.%m.%Y %H:%M")
    except Exception:
        ticket_sell_time = None

    # ticket link
    try:
        if " // " in event.ticket_link:
            event_ticket_link_fi, event_ticket_link_en = event.ticket_link.split(" // ", 1)
            event_ticket_link_fi = event_ticket_link_fi.strip()
            event_ticket_link_en = event_ticket_link_en.strip()
        else:
            event_ticket_link_fi = event.ticket_link
            event_ticket_link_en = event.ticket_link

        event_ticket_link = [event_ticket_link_fi, event_ticket_link_en]


    except:
        event_ticket_link = None

    # event price
    if event.price != 0:
        if event.price.is_integer():
            event_price = f"{int(event.price)} €"
        else:
            event_price = f"{event.price} €"

        text_body += f"{prompts[user_lang_code][7]} {event_price}\n\n"

    if event.price == 0:
        if user_lang_code == 1:
            text_body += "The event is FREE!\n\n"
        else:
            text_body += "Tapahtuma on ilmainen!\n\n"

    # adding if exists
    if event_ticket_link is not None:
        text_body += f"{prompts[user_lang_code][8]} {event_ticket_link[user_lang_code]}"
    if ticket_sell_time is not None:
        text_body += f"\n\n{prompts[user_lang_code][9]} {ticket_sell_time}\n\n"
    if event.other_link is not None:
        text_body += f"{prompts[user_lang_code][10]} {event.other_link}\n\n"

    return text_body


def get_tail(event, user_lang_code):

    if user_lang_code == 0:
        text_tail = f"{event.description_fi}\n\n{event.accessibility_fi}\n\n"
    else:
        text_tail = f"{event.description_en}\n\n{event.accessibility_en}\n\n"

    return text_tail


def event_parser_compact(event, user_lang_code):
    return f"{get_head(event, user_lang_code)} {get_body(event, user_lang_code)}"

def event_parser_normal(event, user_lang_code) -> str:

    return f"{get_head(event, user_lang_code)}{get_body(event, user_lang_code)}{get_tail(event, user_lang_code)}"



def event_parser_all(event) -> str:
    event_text = (
        f"Event: {event.id} "
        f"created by: {event.creator}\n"
        f"Name:{event.name}\n"
        f"starts at: {event.start_time}\n"
        f"ends at: {event.end_time}\n\n"
        f"Location: {event.location}\n"
        f"Finnish description: {event.description_fi}\n\n"
        f"Finnish accessibility: {event.accessibility_fi}\n\n"
        f"English description: {event.description_en}\n\n"
        f"English accessibility:{event.accessibility_en}\n\n"
        f"Price: {event.price}\n"
        f"Tickets: {event.ticket_link}\n"
        f"Ticket sale date: {event.ticket_sell_time}\n"
        f"Dresscode: {event.dc}\n\n"
        f"Tags: {event.tags}")
    return event_text


def get_events_from_backup(user_name: str):
    event_list = events_reader(Filepaths.events_backup_file)
    event_list_to_return = []
    for event in event_list:
        if user_name == event.creator:
            event_list_to_return.append(event)
    return event_list_to_return

def get_event_to_edit(user_name: str):
    event_list = events_reader(Filepaths.events_backup_file)

    for event in event_list:
        if user_name == event.creator and event.stage != 99:
            return event

    return None

def get_event_by_tag(tag: str):
    event_list = get_accepted_events()
    events_to_return = []
    for event in event_list:
        try:
            if any(tag in event_tag or f"#{tag}" in event_tag for event_tag in event.tags):
                events_to_return.append(event)
        except TypeError:
            pass

    return events_to_return

def get_event_by_name_from_backup(event_name):
    event_list = events_reader(Filepaths.events_backup_file)

    for event in event_list:
        if event.name.startswith(event_name):
            return event
    
    return None



def event_backup_save(event, update: Update):


    #this is to avoid backupping the event's that are allready accepted, not having this could lead into duplicate events :D #spagetti
    if event.id != 0:
        return


    event_list = events_reader(Filepaths.events_backup_file)
    new_event_list = []

    for e in event_list:
        if e.name == event.name:
            continue  # Skip the event with the same name
        new_event_list.append(e)

    new_event_list.append(event)

    try:
        with open(Filepaths.events_backup_file, "w") as f:
            json.dump(new_event_list, f, cls=Event.EventEncoder, indent=4, separators=(',', ': '))
            print("Backup made!")

    except FileNotFoundError:
        print("Something went wrong")

def event_backup_delete(event):
    event_list = events_reader(Filepaths.events_backup_file)
    new_event_list = []

    for e in event_list:
        if e.name == event.name:
            continue  # Skip the event with the same creator
        new_event_list.append(e)

    try:
        with open(Filepaths.events_backup_file, "w") as f:
            json.dump(new_event_list, f, cls=Event.EventEncoder, indent=4, separators=(',', ': '))
            print("Backup made!")

    except FileNotFoundError:
        print("Something went wrong")


def get_events_by_creator(update: Update):

    username = update.message.from_user.username

    event_list = get_only_upcoming()
    event_list_to_return = get_events_from_backup(username)


    for event in event_list:
        if username == event.creator:
            event_list_to_return.append(event)

    
    return event_list_to_return

def event_parser_creator_1(event):
    event_text = (
        f"Event: {event.id} "
        f"created by: {event.creator}\n"
        f"Name:{event.name}\n"
        f"starts at: {event.start_time}\n"
        f"ends at: {event.end_time}\n\n"
        f"Location: {event.location}\n"
        f"Finnish description: {event.description_fi}\n\n"
        f"Finnish accessibility: {event.accessibility_fi}\n\n"
        f"Price: {event.price}\n"
        f"Tickets: {event.ticket_link}\n"
        f"Other link: {event.other_link}\n"
        f"Ticket sale date: {event.ticket_sell_time}\n"
        f"Dresscode: {event.dc}\n\n"
        f"Tags: {event.tags}")
    return event_text



def event_parser_creator_2(event):
    event_text = (
        f"English description: {event.description_en}\n\n"
        f"English accessibility:{event.accessibility_en}\n\n"
    )

    return event_text