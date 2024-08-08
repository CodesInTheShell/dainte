from flask import Blueprint, render_template, jsonify, request
from middleware import login_required, rate_limit
from models.irs import InReq
from bson.objectid import ObjectId

import datetime

inreq_blueprint = Blueprint('inreq', __name__)


@inreq_blueprint.route('/api/inreq', methods=['GET'])
@login_required
def inreq(user):
    inreq_id = request.args.get('id')

    if inreq_id:
        # Get a single inreqs by ID
        inreq = InReq.find_by_oid(inreq_id, userId=user.oid)

        if inreq:
            inreq_dict = inreq.to_dict()
            data = {
                "irAnswer": inreq.irAnswer,
                "irQuery": inreq.irQuery,
                "irReferences": inreq.irReferences,
                "projectId": str(inreq.projectId),
                "userId": str(inreq.userId),
                "created": inreq.created.isoformat() if inreq.created else None,
            }
            return jsonify({
                'status': 'success',
                'data': data
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Inreq not found'
            }), 404
    return {'status': 'error', 'message': 'Something went wrong'}
        


@inreq_blueprint.route('/api/inreq-list', methods=['GET'])
@login_required
def list_inreq(user):
    # Get all inreqs
    projectId = request.args.get('projectId')
    inreqs = InReq.find_by_projectId(projectId, userId=user.oid)

    inreq_list = []

    for inreq in inreqs:
        iData = {
            "irAnswer": inreq.irAnswer,
            "irQuery": inreq.irQuery,
            "irReferences": inreq.irReferences,
            "projectId": str(inreq.projectId),
            "userId": str(inreq.userId),
            "created": inreq.created.isoformat() if inreq.created else None,
        }
        inreq_list.append(iData)

    if inreq_list:
        return jsonify({
            'status': 'success',
            'data': inreq_list
        })

    return {'status': 'success', 'data': inreq_list}


@inreq_blueprint.route('/api/inreq-delete', methods=['DELETE'])
@login_required
def inreqDelete(user):

    inreq_id = request.args.get('oid')

    if inreq_id:
        # Get a single inreq by ID
        inreq = InReq.find_by_oid(ObjectId(inreq_id), userId=user.oid)

        if inreq:
            inreq.delete()
            return jsonify({
                'status': 'success',
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'IR not found'
            }), 404
    return {'status': 'error', 'message': 'Something went wrong'}