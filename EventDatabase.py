# This file handles all the handling of the event lists like writing them to events.json file.
# Event creation itself is handled in EventSaver.py


# only_upcoming returns only the upcoming events
# events_reader reads the events.json
# get_unaccepted_events returns events, that have accepted tag as False
# get_accepted_events return events, that have accepted tag as True
# event_parser_normal returns an event text ready to be send to user
# event_parser_all returns an event text with all possible fields. This is used for organizers and admins to check that all event fields are okay
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

import UserDatabase

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_only_upcoming() -> List[Event]:
    event_list = events_reader("events.json")
    event_list_only_upcoming = []
    for event in event_list:
        if event.start_time.date() >= datetime.now().date() and event.end_time == None:
            event_list_only_upcoming.append(event)
        else:
            if event.start_time.date() >= datetime.now().date() and event.end_time > datetime.now():
                event_list_only_upcoming.append(event)

    return event_list_only_upcoming


def events_reader(file_name: str) -> List[Event]:
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


def event_finder_by_id(id: int, file_name) -> Event:
    event_list = events_reader(file_name)
    for event in event_list:
        if int(event.id) == id:
            return event

    return None


def get_unaccepted_events() -> List[Event]:
    event_list = events_reader("events.json")
    unaccepted_events = []
    for event in event_list:
        if not event.accepted:
            unaccepted_events.append(event)

    return unaccepted_events


def get_accepted_events() -> List[Event]:
    event_list = get_only_upcoming()
    accepted_events = []
    for event in event_list:
        if event.accepted:
            accepted_events.append(event)

    return accepted_events


def event_parser_normal(event: Event, user_lang) -> str:
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

    start_time_full = event.start_time

    start_date = start_time_full.strftime("%d.%m.%Y")
    start_time = start_time_full.strftime("%H:%M")

    try:
        end_time_full = event.end_time
        end_date = end_time_full.strftime("%d.%m.%Y")
        end_time = end_time_full.strftime("%H:%M")

        if start_date == end_date:
            text_head = (
                f"{event.name.upper()} - {start_date}\n"
                f"{prompts[lang_code][0]} {start_time} {prompts[lang_code][1]} {end_time}\n")

        if end_date != start_date:
            text_head = (f"**{event.name.upper()}**\n" \
                         f"{prompts[lang_code][2]}\t{start_date} {prompts[lang_code][3]} {start_time}\n"
                         f"{prompts[lang_code][4]}\t{end_date} {prompts[lang_code][5]} {end_time}\n\n")


    except AttributeError:
        text_head = (
            f"**{event.name.upper()}**\n"
            f"{start_date} {prompts[lang_code][6]} {start_time}->\n")

    text_body = (f"{event.location}\nDresscode: {event.dc}\n\n"
                 f"{event.description_fi}\n\n{event.accessibility_fi}\n\n")

    if event.price != 0:
        text_tail = (
            f"{prompts[lang_code][7]} {event.price}\n\n{prompts[lang_code][8]} {event.ticket_link}\n\n{prompts[lang_code][9]} {event.ticket_sell_time}\n\n")

    event_text = f"{text_head}...\n{text_body}{text_tail}"

    return event_text



    """
    if user_lang == "fi":

        start_time_full = event.start_time

        start_date = start_time_full.strftime("%d.%m.%Y")
        start_time = start_time_full.strftime("%H:%M")

        try:
            end_time_full = event.end_time
            end_date = end_time_full.strftime("%d.%m.%Y")
            end_time = end_time_full.strftime("%H:%M")

            if start_date == end_date:
                text_head = (
                    f"{event.name.upper()} - {start_date}\n"
                    f"Klo: {start_time} - {end_time}\n")

            if end_date != start_date:
                text_head = (f"**{event.name.upper()}**\n" \
                             f"Alkaa\t{start_date} klo {start_time}\n"
                             f"Päättyy\t{end_date} klo {end_time}\n\n")


        except AttributeError:
            text_head = (
                f"**{event.name.upper()}**\n"
                f"{start_date} Klo: {start_time}->\n")

        text_body = (f"@{event.location}\nDresscode: {event.dc}\n\n"
                     f"{event.description_fi}\n\n{event.accessibility_fi}\n\n")

        text_tail = (
            f"Hinta: {event.price}\n\nLiput: {event.ticket_link}\n\nLipunmyyntipäivä: {event.ticket_sell_time}\n\n")


        event_text = f"{text_head}...\n{text_body}{text_tail}"


        return event_text

    else:


        start_time_full = event.start_time

        start_date = start_time_full.strftime("%d.%m.%Y")
        start_time = start_time_full.strftime("%H:%M")

        try:
            end_time_full = event.end_time
            end_date = end_time_full.strftime("%d.%m.%Y")
            end_time = end_time_full.strftime("%H:%M")

            if start_date == end_date:
                text_head = (
                    f"{event.name.upper()} - {start_date}\n"
                    f"from {start_time} to {end_time}\n")

            if end_date != start_date:
                text_head = (f"**{event.name.upper()}**\n" \
                             f"Starts\t{start_date} at {start_time}\n"
                             f"Ends\t{end_date} at {end_time}\n\n")


        except AttributeError:
            text_head = (
                f"**{event.name.upper()}**\n"
                f"{start_date} at {start_time}->\n")

        text_body = (f"@{event.location}\nDresscode: {event.dc}\n\n"
                     f"{event.description_fi}\n\n{event.accessibility_fi}\n\n")

        text_tail = (
            f"Price: {event.price}\n\nTickets: {event.ticket_link}\n\nTicket sale: {event.ticket_sell_time}\n\n")

        event_text = f"{text_head}...\n{text_body}{text_tail}"


        return event_text
        """


def event_parser_all(event: Event) -> str:
    event_text = (
        f"Id: {event.id}\n{event.name} - starts at: {event.start_time}\nends at: {event.end_time}\n\nLocation: {event.location}\n"
        f"Finnish description: {event.description_fi}\n\nFinnish accessibility: {event.accessibility_fi}\n\n"
        f"English description: {event.description_en}\n\nEnglish accessibility:{event.accessibility_en}\n\n"
        f"Price: {event.price}\n\nTickets: {event.ticket_link}\n\nTicket sale date: {event.ticket_sell_time}\n\nDresscode: {event.dc}")
    return event_text


def get_event_to_edit(user_name: str) -> Event:
    event_list: List[Event] = events_reader("events_backup.json")
    for event in event_list:
        if user_name == event.creator:
            return event
    return None





def event_backup_save(event: Event, update: Update):
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
