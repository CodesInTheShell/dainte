from models import db
from bson.objectid import ObjectId


import datetime
import logging
import os




inReq_collection = db['inReq'] 


class InReq:
    ATTRS = [
        # "oid", Do not include oid on ATTRS
        "irQuery",
        "irAnswer",
        "irReferences",
        "userId",
        "created",
        "projectId",
    ]
    def __init__(self, oid=None):
        self.oid = oid
        self.irAnswer = None
        self.irQuery = None
        self.irReferences = []
        self.userId = None 
        self.created = 0 
        self.projectId = None

    @staticmethod
    def from_dict(data):
        inreq = InReq(oid=data.get('_id'))
        for attr in InReq.ATTRS:
            setattr(inreq, attr, data.get(attr))
        return inreq

    def to_dict(self, includeOid=True):
        data = {
            "irAnswer": self.irAnswer,
            "irQuery": self.irQuery,
            "irReferences": self.irReferences,
            "projectId": self.projectId,
            "userId": self.userId,
            "created": self.created,
        }

        if includeOid:
            if self.oid:
                data['oid'] = self.oid
        return data
    
    def save(self):
        """Save to mongodb"""
        if self.oid:
            inReq_collection.update_one({"_id": self.oid}, {"$set": self.to_dict(includeOid=False)}, upsert=True)
        else:
            self.oid = inReq_collection.insert_one(self.to_dict()).inserted_id
        return self

    @staticmethod
    def find_by_oid(oid, userId=None):
        query = {"_id": oid}
        if userId:
            query['userId'] = userId
        data = inReq_collection.find_one({"_id": oid})
        if data:
            return  InReq.from_dict(data)
        return None
    
    def delete(self):
        inReq_collection.delete_one({"_id": self.oid, "userId": self.userId})
    
    @staticmethod
    def find_all(userId=None):
        query = {}
        if userId:
            query['userId'] = userId
        data = inReq_collection.find(query)
        return [InReq.from_dict(inreq) for inreq in data]
    
    @staticmethod
    def find_by_projectId(projectId, userId=None):
        query = {'projectId': ObjectId(projectId)}
        if userId:
            query['userId'] = userId
        data = inReq_collection.find(query)
        return [InReq.from_dict(inreq) for inreq in data]
    
    

