import json



class Like:
    def __init__(self, id: int, likers=[]):
        self.id = id
        self.likers = likers



    def to_dict(self):
        return {
            "id": self.id,
            "likers": self.likers
        }



class LikeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Like):
            return obj.to_dict()
        return super().default(obj)