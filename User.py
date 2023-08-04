import json

class User:
    def __init__(self, id, nick, tags, user_type, user_lang=None):
        self.id = id
        self.nick = nick
        self.tags = tags
        self.user_type = user_type
        self.user_lang = user_lang

    def to_json(self):
        return self.__dict__

class CustomerEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, User):
            return obj.__dict__
        return super().default(obj)