from models import db
import datetime

users_collection = db['users'] 

from werkzeug.security import generate_password_hash, check_password_hash

class User:
    ATTRS = [
        # "oid", Do not include oid on ATTRS
        "username",
        "password",
        "api_calls",
        "last_reset",
        "tokenAvailable",
    ]
    def __init__(self, oid=None):
        self.oid = oid
        self.username = None
        self.password = None
        self.api_calls = 0 # number of AI api analysis calls
        self.last_reset = datetime.datetime.now() # date last api call
        self.tokenAvailable = 0 # decrement as they receive prompt reponse by total_token_count

    @staticmethod
    def from_dict(data):
        user = User(oid=data.get('_id'))
        for attr in User.ATTRS:
            setattr(user, attr, data.get(attr))
        return user

    def to_dict(self, includeOid=True):
        data = {
            "username": self.username,
            "password": self.password,
            "api_calls": self.api_calls,
            "last_reset": self.last_reset,
            "tokenAvailable": self.tokenAvailable,
        }

        if includeOid:
            if self.oid:
                data['oid'] = self.oid
        return data
    
    def save(self):
        if self.oid:
            users_collection.update_one({"_id": self.oid}, {"$set": self.to_dict(includeOid=False)}, upsert=True)
        else:
            self.oid = users_collection.insert_one(self.to_dict()).inserted_id
        return self
    
    @staticmethod
    def create(username, password):
        if User.find_by_username(username):
            raise ValueError("Username already exists")
        
        user = User()
        user.username = username
        user.password = generate_password_hash(password)
        user.save()
        return user

    @staticmethod
    def find_by_username(username):
        user_data = users_collection.find_one({"username": username})
        if user_data:
            return  User.from_dict(user_data)
        return None

    def update_password(self, new_password):
        self.password = generate_password_hash(new_password)
        users_collection.update_one({"username": self.username}, {"$set": {"password": self.password}})
    
    def delete(self):
        users_collection.delete_one({"username": self.username})
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def increment_api_calls(self):
        now = datetime.datetime.now()
        if now - self.last_reset > datetime.timedelta(days=1):
            self.api_calls = 1
            self.last_reset = now
        else:
            self.api_calls += 1
        users_collection.update_one({"_id": self.oid}, {"$set": {"api_calls": self.api_calls, "last_reset": self.last_reset}})

    def check_rate_limit(self, max_calls_per_day):
        now = datetime.datetime.now()
        
        if now - self.last_reset > datetime.timedelta(days=1):
            self.api_calls = 0
            self.last_reset = now
            users_collection.update_one({"_id": self.oid}, {"$set": {"api_calls": self.api_calls, "last_reset": self.last_reset}})
        return self.api_calls < max_calls_per_day
    
    def decrementTokenAvailableBy(self, num):
        self.tokenAvailable = self.tokenAvailable - num
        self.save()
    
    def increaseTokenAvailableBy(self, num):
        self.tokenAvailable = self.tokenAvailable + num
        self.save()
    
    def setTokenAvailableBy(self, num):
        """Set or reset the user tokenAvailable"""
        self.tokenAvailable = num
        self.save()
