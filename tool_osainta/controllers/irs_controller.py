import os

from models.irs import InReq 
from bson.objectid import ObjectId
import datetime

class InReqController:
    """
    """
    
    def __init__(self):
        pass
    
    @staticmethod
    def saveIr(data, userId):
        dictData = {
            "irAnswer": data.get('irAnswer'),
            "irQuery": data.get('irQuery'),
            "irReferences": data.get('irReferences'),
            "projectId": ObjectId(data.get('projectId')),
            "userId": userId,
            "created": datetime.datetime.now(),
        }
        irreq = InReq.from_dict(dictData)
        irreq.save()