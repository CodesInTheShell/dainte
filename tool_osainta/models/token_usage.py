from models import db
import datetime

token_usage_collection = db['token_usage'] 

from werkzeug.security import generate_password_hash, check_password_hash

class TokenUsage:
    ATTRS = [
        "prompt_token_count",
        "candidates_token_count",
        "total_token_count",
        "userId",
        "created",
        # "oid", Do not include oid on ATTRS

    ]
    def __init__(self, oid=None):
        self.oid = oid
        self.prompt_token_count = 0
        self.candidates_token_count = 0
        self.total_token_count = 0
    
    @staticmethod
    def from_dict(data):
        tku = TokenUsage(oid=data.get('_id'))
        for attr in TokenUsage.ATTRS:
            setattr(tku, attr, data.get(attr))
        return tku
    
    def to_dict(self, includeOid=True):
        data = {
            "prompt_token_count": self.prompt_token_count,
            "candidates_token_count": self.candidates_token_count,
            "total_token_count": self.total_token_count,
            "userId": self.userId,
            "created": self.created,
        }
        if includeOid:
            if self.oid:
                data['oid'] = self.oid
        return data
    
    def save(self):
        if self.oid:
            token_usage_collection.update_one({"_id": self.oid}, {"$set": self.to_dict(includeOid=False)}, upsert=True)
        else:
            self.oid = token_usage_collection.insert_one(self.to_dict()).inserted_id
        return self
    
    def delete(self):
        token_usage_collection.delete_one({"_id": self.oid})
    
    @staticmethod
    def create(userId, genai_respone_obj):
        tku = TokenUsage()
        tku.prompt_token_count = genai_respone_obj.usage_metadata.prompt_token_count
        tku.candidates_token_count = genai_respone_obj.usage_metadata.candidates_token_count
        tku.total_token_count = genai_respone_obj.usage_metadata.total_token_count
        tku.userId = userId
        tku.created = datetime.datetime.now()
        tku.save()
        return tku
        