from flask import Blueprint, render_template, jsonify, request
from middleware import login_required, rate_limit
from models.knowledge import Knowledge
from bson.objectid import ObjectId
from controllers import knowledge_controller

import datetime

knowledge_blueprint = Blueprint('knowledge', __name__)


@knowledge_blueprint.route('/api/knowledge', methods=['GET'])
@login_required
def knowledge(user):
    knowledge_id = request.args.get('id')

    if knowledge_id:
        # Get a single knowledge by ID
        knowledge = Knowledge.find_by_oid(knowledge_id, userId=user.oid)

        if knowledge:
            knowledge_dict = knowledge.to_dict()
            data = {
                "name": knowledge.name,
                "description": knowledge.description,
                "data": knowledge.data,
                "oid": str(knowledge.oid),
                "userId": str(knowledge.userId),
                "created": knowledge.created.isoformat() if knowledge.created else None,
            }
            return jsonify({
                'status': 'success',
                'data': data
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Knowledge not found'
            }), 404
    return {'status': 'error', 'message': 'Something went wrong'}
        


@knowledge_blueprint.route('/api/knowledge-list', methods=['GET'])
@login_required
def list_knowledge(user):
    # Get all knowledges
    includeData = request.args.get('includeData', 'no')

    knowledges = Knowledge.find_all(userId=user.oid)

    knowledge_list = []

    for knowledge in knowledges:
        kData = {
            "name": knowledge.name,
            "description": knowledge.description,
            "created": knowledge.created.isoformat() if knowledge.created else None,
            "oid": str(knowledge.oid),
            "userId": str(knowledge.userId),
        }
        if includeData:
            kData['data'] = knowledge.data
        knowledge_list.append(kData)

    if knowledge_list:
        return jsonify({
            'status': 'success',
            'data': knowledge_list
        })

    return {'status': 'error', 'data': knowledge_list}

@knowledge_blueprint.route('/api/knowledge', methods=['POST'])
@login_required
@rate_limit
def knowledgePost(user):

    # limit to 100000 estimate words for now
    def get_first_100000_words(text):
        words = text.split()
        first_100000_words = words[:100000]
        result_text = ' '.join(first_100000_words)
        
        return result_text
    
    data = request.get_json()

    knowledgeName = data.get('knowledgeName')
    knowledgeDescription = data.get('knowledgeDescription')
    knowledgeData = get_first_100000_words(data.get('knowledgeData'))

    knowledge = Knowledge.from_dict({
        "name": knowledgeName,
        "description": knowledgeDescription,
        "data": knowledgeData,
        "userId": user.oid,
        "pointIds": [],
        "created": datetime.datetime.now(),
    })
    knowledge.save()
    knowledge.storeEmbeddings()

    knowledge = Knowledge.find_by_oid(ObjectId(knowledge.oid), userId=user.oid)
    data = {
        "name": knowledge.name,
        "description": knowledge.description,
        "data": knowledge.data,
        "pointIds": knowledge.pointIds,
        "userId": str(knowledge.userId),
        "created": knowledge.created.isoformat(),
        "oid": str(knowledge.oid)
    }
    
    return jsonify({
        'status': 'success',
        'data': data
    })


@knowledge_blueprint.route('/api/knowledge-delete', methods=['DELETE'])
@login_required
def knowledgeDelete(user):

    knowledge_id = request.args.get('oid')

    if knowledge_id:
        # Get a single knowledge by ID
        knowledge = Knowledge.find_by_oid(ObjectId(knowledge_id), userId=user.oid)

        if knowledge:
            knowledge.delete()
            return jsonify({
                'status': 'success',
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Knowledge not found'
            }), 404
    return {'status': 'error', 'message': 'Something went wrong'}