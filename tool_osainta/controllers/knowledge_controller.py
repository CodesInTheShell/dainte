import os
import google.generativeai as genai

from models.knowledge import Knowledge 
from bson.objectid import ObjectId



# genai.configure(api_key=os.environ.get('OSAINTA_GEMINI_API_KEY'))

OSAINTA_EMBEDDING_MODEL = os.environ.get('OSAINTA_EMBEDDING_MODEL', 'models/text-embedding-004')


class KnowledgeController:
    """
    from controllers.knowledge_controller import KnowledgeController
    KnowledgeController.getReferences('What are Text embeddings ?', '66a9c4f50490e35bf7d67***')
    """
    
    def __init__(self):
        pass
    
    @staticmethod
    def getReferences(query_input, userId,  num=2):

        ragReferences = []

        result = genai.embed_content(
                model=OSAINTA_EMBEDDING_MODEL,
                content=query_input,
                task_type="retrieval_document",
                # title=self.name
            )        
        embedding = result['embedding']

        similars = Knowledge.findSimilarity(embedding, userId,  num=2)
        
        return similars
    
    @staticmethod
    def forRagInject(similars):

        if len(similars) < 0:
            return ''
        
        ragReferences = [sim.payload.get('chunk', '') for sim in similars]

        textForPrompt = 'ADDITIONAL INFORMATION:\n'
        for ref in ragReferences:
            textForPrompt += ref + '\n\n'
        
        return textForPrompt
    
    @staticmethod
    def kvKnowledge(similars):
        """
        Return knowledge name and the chunk value pair
        """
        kvs = []

        for ref in similars:
            knowledge = Knowledge.find_by_oid(ObjectId(ref.payload.get('knowledgeId')))
            kvs.append({
                'knowledgeName': knowledge.name,
                'chunk': ref.payload.get('chunk', '')
            })

        return kvs









 
