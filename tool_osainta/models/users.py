from models import db
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urljoin

import secrets
import os
import datetime

users_collection = db['users'] 

class User:
    ATTRS = [
        # "oid", Do not include oid on ATTRS
        "username",
        "password",
        "api_calls",
        "last_reset",
        "tokenAvailable",
        "reset_token",
        "reset_token_expiry",
    ]
    def __init__(self, oid=None):
        self.oid = oid
        self.username = None
        self.password = None
        self.api_calls = 0 # number of AI api analysis calls
        self.last_reset = datetime.datetime.now() # date last api call
        self.tokenAvailable = 0 # decrement as they receive prompt reponse by total_token_count
        self.reset_token = None
        self.reset_token_expiry = None


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
            "reset_token": self.reset_token,
            "reset_token_expiry": self.reset_token_expiry,
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
    
    @staticmethod
    def generate_reset_password_link(username, base_url, forgot_password=False):
        user = User.find_by_username(username)
        if not user:
            return None
        
        reset_token = secrets.token_urlsafe(32)
       
        if forgot_password:
            users_collection.update_one({"username": username}, {"$set": {"reset_token": reset_token, "reset_token_expiry": datetime.datetime.utcnow() + datetime.timedelta(hours=48)}})
            reset_link = urljoin(base_url, f"/set_password?token={reset_token}&username={username}")
        else:
            users_collection.update_one({"username": username}, {"$set": {"reset_token": reset_token, "reset_token_expiry": datetime.datetime.utcnow() + datetime.timedelta(hours=24)}})
            reset_link = urljoin(base_url, f"/reset_password?token={reset_token}&username={username}")
        return reset_link
    
    @staticmethod
    def reset_password(reset_token, new_password, username):
        user = User.find_by_username(username)
        if not user:
            return False
        if user.reset_token == reset_token and user.reset_token_expiry > datetime.datetime.utcnow():
            user.update_password(new_password)
            users_collection.update_one({"username": username}, {"$set": {"reset_token": None, "reset_token_expiry": None}})
            return True
        else:
            return False

