import json
from datetime import datetime


#this is the class for event objects

class Event:

    def __init__(self, id: int, creator, name=None, start_time=None, end_time=None, ticket_sell_time=None,
                 location=None, description_fi=None, description_en=None, ticket_link=None, other_link=None,
                 accessibility_fi=None, accessibility_en=None, price=None, dc=None, accepted=False, tags=[], stage=None):
        self.id = id
        self.name = name
        self.creator = creator
        self.start_time = start_time if isinstance(start_time, datetime) else datetime.strptime(start_time,
                                                                                                "%Y-%m-%d %H:%M:%S") if start_time else None
        self.end_time = end_time if isinstance(end_time, datetime) else datetime.strptime(end_time,
                                                                                          "%Y-%m-%d %H:%M:%S") if end_time else None
        self.ticket_sell_time = ticket_sell_time if isinstance(ticket_sell_time, datetime) else datetime.strptime(ticket_sell_time,
                                                                                          "%Y-%m-%d %H:%M:%S") if ticket_sell_time else None
        self.location = location
        self.description_fi = description_fi
        self.description_en = description_en
        self.ticket_link = ticket_link
        self.other_link = other_link
        self.accessibility_fi = accessibility_fi
        self.accessibility_en = accessibility_en
        self.price = price
        self.dc = dc
        self.accepted = accepted
        self.tags = tags
        self.stage = stage

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "creator": self.creator,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S") if self.start_time else None,
            "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else None,
            "ticket_sell_time": self.ticket_sell_time.strftime("%Y-%m-%d %H:%M:%S") if self.ticket_sell_time else None,
            "location": self.location,
            "description_fi": self.description_fi,
            "description_en": self.description_en,
            "ticket_link": self.ticket_link,
            "other_link": self.other_link,
            "accessibility_fi": self.accessibility_fi,
            "accessibility_en": self.accessibility_en,
            "price": self.price,
            "dc": self.dc,
            "accepted": self.accepted,
            "tags": self.tags,
            "stage": self.stage
        }




class EventEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Event):
            return obj.to_dict()
        return super().default(obj)