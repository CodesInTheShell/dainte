from models import db
from bson.objectid import ObjectId


import datetime
import logging
import os


projects_collection = db['projects'] 


class Project:
    ATTRS = [
        # "oid", Do not include oid on ATTRS
        "name",
        "description",
        "userId",
        "created",
        "suggestedSearchLinks",
    ]
    def __init__(self, oid=None):
        self.oid = oid
        self.name = None
        self.description = None
        self.userId = None 
        self.created = 0 
        self.suggestedSearchLinks = []

    @staticmethod
    def from_dict(data):
        project = Project(oid=data.get('_id'))
        for attr in Project.ATTRS:
            setattr(project, attr, data.get(attr))
        return project

    def to_dict(self, includeOid=True):
        data = {
            "name": self.name,
            "description": self.description,
            "userId": self.userId,
            "created": self.created,
            "suggestedSearchLinks": self.suggestedSearchLinks
        }

        if includeOid:
            if self.oid:
                data['oid'] = self.oid
        return data
    
    def save(self):
        """Save to mongodb"""
        if self.oid:
            projects_collection.update_one({"_id": self.oid}, {"$set": self.to_dict(includeOid=False)}, upsert=True)
        else:
            self.oid = projects_collection.insert_one(self.to_dict()).inserted_id
        return self

    @staticmethod
    def find_by_oid(oid, userId=None):
        query = {"_id": oid}
        if userId:
            query['userId'] = userId
        data = projects_collection.find_one({"_id": oid})
        if data:
            return  Project.from_dict(data)
        return None
    
    def delete(self):
        projects_collection.delete_one({"_id": self.oid, "userId": self.userId})
    
    @staticmethod
    def find_all(userId=None):
        query = {}
        if userId:
            query['userId'] = userId
        data = projects_collection.find(query)
        return [Project.from_dict(project) for project in data]
    
    

