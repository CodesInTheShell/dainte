from models import db
from bson.objectid import ObjectId


import datetime
import logging
import os


reports_collection = db['reports'] 


class Report:
    ATTRS = [
        # "oid", Do not include oid on ATTRS
        "name",
        "content",
        "userId",
        "created",
        "projectId",
    ]
    def __init__(self, oid=None):
        self.oid = oid
        self.name = None
        self.content = None
        self.userId = None 
        self.created = 0 
        self.projectId = None

    @staticmethod
    def from_dict(data):
        report = Report(oid=data.get('_id'))
        for attr in Report.ATTRS:
            setattr(report, attr, data.get(attr))
        return report

    def to_dict(self, includeOid=True):
        data = {
            "name": self.name,
            "content": self.content,
            "userId": self.userId,
            "created": self.created,
            "projectId": self.projectId
        }

        if includeOid:
            if self.oid:
                data['oid'] = self.oid
        return data
    
    def save(self):
        """Save to mongodb"""
        if self.oid:
            reports_collection.update_one({"_id": self.oid}, {"$set": self.to_dict(includeOid=False)}, upsert=True)
        else:
            self.oid = reports_collection.insert_one(self.to_dict()).inserted_id
        return self

    @staticmethod
    def find_by_oid(oid, userId=None):
        query = {"_id": oid}
        if userId:
            query['userId'] = userId
        data = reports_collection.find_one({"_id": oid})
        if data:
            return  Report.from_dict(data)
        return None
    
    def delete(self):
        reports_collection.delete_one({"_id": self.oid, "userId": self.userId})
    
    @staticmethod
    def find_all(projectId=None, userId=None):
        query = {}
        if userId:
            query['userId'] = userId
        if projectId:
            query['projectId'] = userId
        data = reports_collection.find(query)
        return [Report.from_dict(report) for report in data]
    
    

