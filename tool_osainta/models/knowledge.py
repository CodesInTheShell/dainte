from models import db
import datetime
from bson.objectid import ObjectId
from models import q_client, QDRANT_EMBEDDING_COLLECTION_NAME
import google.generativeai as genai
from qdrant_client.models import PointStruct
import uuid
from osainta_core import split_text
import logging
from qdrant_client.models import PointIdsList, Filter, FieldCondition, MatchValue
import os

OSAINTA_EMBEDDING_MODEL = os.environ.get('OSAINTA_EMBEDDING_MODEL', 'models/text-embedding-004')


knowledge_collection = db['knowledge'] 


class Knowledge:
    ATTRS = [
        # "oid", Do not include oid on ATTRS
        "name",
        "description",
        "data",
        "userId",
        "created",
        "pointIds",
    ]
    def __init__(self, oid=None):
        self.oid = oid
        self.name = None
        self.description = None
        self.data = 0 
        self.userId = None 
        self.created = 0 
        self.pointIds = []

    @staticmethod
    def from_dict(data):
        knowledge = Knowledge(oid=data.get('_id'))
        for attr in Knowledge.ATTRS:
            setattr(knowledge, attr, data.get(attr))
        return knowledge

    def to_dict(self, includeOid=True):
        data = {
            "name": self.name,
            "description": self.description,
            "data": self.data,
            "userId": self.userId,
            "created": self.created,
            "pointIds": self.pointIds
        }

        if includeOid:
            if self.oid:
                data['oid'] = self.oid
        return data
    
    def save(self):
        """Save to mongodb"""
        if self.oid:
            knowledge_collection.update_one({"_id": self.oid}, {"$set": self.to_dict(includeOid=False)}, upsert=True)
        else:
            self.oid = knowledge_collection.insert_one(self.to_dict()).inserted_id
        return self

    @staticmethod
    def find_by_oid(oid, userId=None):
        query = {"_id": oid}
        if userId:
            query['userId'] = userId
        data = knowledge_collection.find_one({"_id": oid})
        if data:
            return  Knowledge.from_dict(data)
        return None
    
    @staticmethod
    def deleteQdrantByIds(ids):
        q_client.delete(
            collection_name=QDRANT_EMBEDDING_COLLECTION_NAME,
            points_selector=PointIdsList(
                points=ids
            )
        )

    def delete(self, deleteQdrant=True):
        if deleteQdrant:
            if self.pointIds and len(self.pointIds) > 0:
                Knowledge.deleteQdrantByIds(self.pointIds)
            logging.info(f'Deleting knowledge {self.oid} but no qdrant points')
        knowledge_collection.delete_one({"_id": self.oid, "userId": self.userId})
    
    @staticmethod
    def find_all(userId=None):
        query = {}
        if userId:
            query['userId'] = userId
        data = knowledge_collection.find(query)
        return [Knowledge.from_dict(knowledge) for knowledge in data]
    
    def storeEmbeddings(self):
        """Call this after the save method."""

        if not self.oid or not self.userId:
            raise Exception("Knowledge oid and userId are required")
        
        operation_info = None

        split_data = split_text(self.data, chunk_size=300, overlap=80)

        new_pointIds = []

        for chunk in split_data:

            pointId = str(uuid.uuid4())

            result = genai.embed_content(
                model=OSAINTA_EMBEDDING_MODEL,
                content=chunk,
                task_type="retrieval_document",
                title=self.name
            )        
            operation_info = q_client.upsert(
                collection_name=QDRANT_EMBEDDING_COLLECTION_NAME,
                wait=True,
                points=[
                    PointStruct(
                    id=pointId,
                    vector=result['embedding'],
                    payload={
                        'userId': str(self.userId),
                        'knowledgeId': str(self.oid),
                        'chunk': chunk,
                        }
                    )
                ]
            )
            new_pointIds.append(pointId)
        
        if new_pointIds:
            self.pointIds += new_pointIds
            self.save()
        
        return operation_info
    
    @staticmethod
    def findSimilarity(embedding, userId,  num=2, score_threshold=0.5):

        search_result = q_client.search(
            collection_name=QDRANT_EMBEDDING_COLLECTION_NAME,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="userId",
                        match=MatchValue(
                            value=userId,
                        ),
                    )
                ]
            ),
            query_vector=embedding,
            limit=num,
            score_threshold=score_threshold
        )
        return search_result

