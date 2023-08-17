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

from Event import Event
import logging

import UserDatabase

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_only_upcoming():
    event_list = events_reader("events.json")
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

            # Gets the start and end times and turns them into datetime objects
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S") if start_time_str else None
            end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S") if end_time_str else None

            event_object = Event.Event(
                event_data['id'],
                event_data['creator'],
            )
            event_object.name = event_data['name']
            event_object.start_time = start_time
            event_object.end_time = end_time
            event_object.ticket_sell_time = event_data['ticket_sell_time']
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
                event_object.tags = ["#all"]
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

    return event_list


def events_writer(event_list):
    try:
        with open("events.json", "w") as f:
            json.dump(event_list, f, cls=Event.EventEncoder, indent=4, separators=(',', ': '))
            print("Event saved")


    except FileNotFoundError:
        print("Something went wrong")


def event_finder_by_id(id: int, file_name):
    event_list = events_reader(file_name)
    for event in event_list:
        if int(event.id) == id:
            return event

    return None


def get_unaccepted_events():
    event_list = events_reader("events.json")
    unaccepted_events = []
    for event in event_list:
        if not event.accepted:
            unaccepted_events.append(event)

    return unaccepted_events


def get_accepted_events():
    event_list = get_only_upcoming()
    accepted_events = []
    for event in event_list:
        if event.accepted:
            accepted_events.append(event)

    return accepted_events

def get_head(id: int, user_lang) -> str:
    prompts = [["from", "to", "Starts", "at", "Ends", "at", "at", "Price", "Tickets: ", "Ticket sale time"],
               ["Klo: ", "-", "Alkaa", "klo", "Päättyy", "klo", "klo: ", "Hinta: ", "Liput", "Lipunmyyntipäivä"]]


    #set lang_code so we can point to correct lang version in prompt
    if user_lang == "fi":
        lang_code = 1
    else:
        lang_code = 0


    event_list = get_accepted_events()
    for event in event_list:
        if id == event.id:
            event_name_fi = ""
            event_name_eng = ""

            if "//" in event.name:
                event_name_fi, event_name_eng = event.name.split("//", 1)
                event_name_fi = event_name_fi.strip()
                event_name_eng = event_name_eng.strip()
            else:
                event_name_fi = event.name
                event_name_eng = event.name

            event_name = [event_name_eng, event_name_fi]

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
                        f"{event_name[lang_code].upper()} - {start_date}\n"
                        f"{prompts[lang_code][0]} {start_time} {prompts[lang_code][1]} {end_time}\n")

                if end_date != start_date:
                    text_head = (f"**{event_name[lang_code].upper()}**\n" \
                                 f"{prompts[lang_code][2]}\t{start_date} {prompts[lang_code][3]} {start_time}\n"
                                 f"{prompts[lang_code][4]}\t{end_date} {prompts[lang_code][5]} {end_time}\n\n")


            except AttributeError:
                text_head = (
                    f"**{event_name[lang_code].upper()}**\n"
                    f"{start_date} {prompts[lang_code][6]} {start_time}->\n")

            return text_head





def event_parser_normal(event, user_lang) -> str:
    # contains name and time
    prompts = [["from", "to", "Starts", "at", "Ends", "at", "at", "Price","Tickets: ", "Ticket sale time"],
               ["Klo: ", "-", "Alkaa", "klo", "Päättyy", "klo", "klo: ","Hinta: ", "Liput", "Lipunmyyntipäivä"]]

    if user_lang == "fi":
        lang_code = 1
    else:
        lang_code = 0

    text_head = ""

    # Contains location, drescode, description and accesibility information
    text_body = ""

    # contains ticket information
    text_tail = ""



    if "//" in event.name:
        event_name_fi, event_name_en = event.name.split("//", 1)
        event_name_fi = event_name_fi.strip()
        event_name_en = event_name_en.strip()
    else:
        event_name_fi = event.name
        event_name_en = event.name

    event_name = [event_name_en, event_name_fi]


    start_time_full = event.start_time

    start_date = start_time_full.strftime("%d.%m.%Y")
    start_time = start_time_full.strftime("%H:%M")

    try:
        end_time_full = event.end_time
        end_date = end_time_full.strftime("%d.%m.%Y")
        end_time = end_time_full.strftime("%H:%M")

        if start_date == end_date:
            text_head = (
                f"{event_name[lang_code].upper()} - {start_date}\n"
                f"{prompts[lang_code][0]} {start_time} {prompts[lang_code][1]} {end_time}\n")

        if end_date != start_date:
            text_head = (f"**{event_name[lang_code].upper()}**\n" \
                         f"{prompts[lang_code][2]}\t{start_date} {prompts[lang_code][3]} {start_time}\n"
                         f"{prompts[lang_code][4]}\t{end_date} {prompts[lang_code][5]} {end_time}\n\n")


    except AttributeError:
        text_head = (
            f"**{event_name[lang_code].upper()}**\n"
            f"{start_date} {prompts[lang_code][6]} {start_time}->\n")

    if "//" in event.dc:
        event_dc_fi, event_dc_en = event.dc.split("//", 1)
        event_dc_fi = event_dc_fi.strip()
        event_dc_en = event_dc_en.strip()
    else:
        event_dc_fi = event.dc
        event_dc_en = event.dc

    if "//" in event.location:
        event_location_fi, event_location_en = event.location.split("//", 1)
        event_location_fi = event_location_fi.strip()
        event_location_en = event_location_en.strip()
    else:
        event_location_fi = event.location
        event_location_en = event.location

    if lang_code == 1:
        text_body = (f"Tapahtumapaikka: {event_location_fi}\nDresscode: {event_dc_fi}\n\n"
                     f"{event.description_fi}\n\n{event.accessibility_fi}\n\n")

    elif lang_code == 0:
        text_body = (f"Location: {event_location_en}\nDresscode: {event_dc_en}\n\n"
                     f"{event.description_en}\n\n{event.accessibility_en}\n\n")


    try:
        if "//" in event.ticket_link:
            event_ticket_link_fi, event_ticket_link_en = event.ticket_link.split("//", 1)
            event_ticket_link_fi = event_ticket_link_fi.strip()
            event_ticket_link_en = event_ticket_link_en.strip()
        else:
            event_ticket_link_fi = event.ticket_link
            event_ticket_link_en = event.ticket_link

        event_ticket_link = [event_ticket_link_en, event_ticket_link_fi]


    except:
        event_ticket_link = None


    if event.price != 0:
        text_tail += f"{prompts[lang_code][7]} {event.price}\n\n"
    if event.price == 0:
        if lang_code == 0:
            text_tail += "The event is FREE!\n\n"
        elif lang_code == 1:
            text_tail += "Tapahtuma on ilmainen!\n\n"

    if event_ticket_link is not None:
        text_tail += f"{prompts[lang_code][8]} {event_ticket_link[lang_code]}"
    if event.ticket_sell_time is not None:
        text_tail += f"\n\n{prompts[lang_code][9]} {event.ticket_sell_time}\n\n"

    event_text = f"{text_head}...\n{text_body}{text_tail}"

    return event_text



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


def get_event_to_edit(user_name: str):
    event_list: List[Event] = events_reader("events_backup.json")
    for event in event_list:
        if user_name == event.creator:
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



def event_backup_save(event, update: Update):
    event_list: List[Event] = events_reader("events_backup.json")
    new_event_list: List[Event] = []

    for e in event_list:
        if e.creator == update.message.from_user.username:
            continue  # Skip the event with the same creator
        new_event_list.append(e)

    new_event_list.append(event)

    try:
        with open("events_backup.json", "w") as f:
            json.dump(new_event_list, f, cls=Event.EventEncoder, indent=4, separators=(',', ': '))
            print("Backup made!")

    except FileNotFoundError:
        print("Something went wrong")

def event_backup_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_list: List[Event] = events_reader("events_backup.json")
    new_event_list: List[Event] = []

    for e in event_list:
        if e.creator == update.message.from_user.username:
            continue  # Skip the event with the same creator
        new_event_list.append(e)

    try:
        with open("events_backup.json", "w") as f:
            json.dump(new_event_list, f, cls=Event.EventEncoder, indent=4, separators=(',', ': '))
            print("Backup made!")

    except FileNotFoundError:
        print("Something went wrong")
