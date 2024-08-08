from flask import Blueprint, render_template, jsonify, request
from middleware import login_required, rate_limit
from models.projects import Project
from bson.objectid import ObjectId
from osainta_core import generateSuggestedLinks

import json
import datetime

project_blueprint = Blueprint('project', __name__)


@project_blueprint.route('/api/project', methods=['GET'])
@login_required
def project(user):
    project_id = request.args.get('id')

    if project_id:
        # Get a single projects by ID
        project = Project.find_by_oid(project_id, userId=user.oid)

        if project:
            project_dict = project.to_dict()
            data = {
                "name": project.name,
                "description": project.description,
                "oid": str(project.oid),
                "userId": str(project.userId),
                "created": project.created.isoformat() if project.created else None , 
                "suggestedSearchLinks": project.suggestedSearchLinks,
            }
            return jsonify({
                'status': 'success',
                'data': data
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
    return {'status': 'error', 'message': 'Something went wrong'}
        


@project_blueprint.route('/api/project-list', methods=['GET'])
@login_required
def list_projects(user):
    # Get all projects
    projects = Project.find_all(userId=user.oid)

    project_list = []

    for project in projects:
        pData = {
            "name": project.name,
            "description": project.description,
            "created": project.created.isoformat(),
            "oid": str(project.oid),
            "userId": str(project.userId),
            "suggestedSearchLinks": project.suggestedSearchLinks,
        }
        project_list.append(pData)

    if project_list:
        return jsonify({
            'status': 'success',
            'data': project_list
        })

    return {'status': 'success', 'data': project_list}

@project_blueprint.route('/api/project', methods=['POST'])
@login_required
@rate_limit
def projectPost(user):
    
    data = request.get_json()

    projectName = data.get('projectName')
    projectDescription = data.get('projectDescription')

    suggestedSearchLinksItems = []
    links_result_obj = generateSuggestedLinks({'projectName': projectName, 'projectDescription': projectDescription})
    user.decrementTokenAvailableBy(links_result_obj.usage_metadata.total_token_count)
    suggestedSearchLinks = json.loads(links_result_obj.text)

    if len(suggestedSearchLinks) > 0:
        for l in suggestedSearchLinks:
            suggestedSearchLinksItems.append(l['search_link'])

    project = Project.from_dict({
        "name": projectName,
        "description": projectDescription,
        "userId": user.oid,
        "suggestedSearchLinks": suggestedSearchLinksItems,
        "created": datetime.datetime.now(),
    })
    project.save()

    project = Project.find_by_oid(ObjectId(project.oid), userId=user.oid)
    data = {
        "name": project.name,
        "description": project.description,
        "suggestedSearchLinks": project.suggestedSearchLinks,
        "userId": str(project.userId),
        "created": project.created.isoformat(),
        "oid": str(project.oid)
    }
    
    return jsonify({
        'status': 'success',
        'data': data
    })


@project_blueprint.route('/api/project-delete', methods=['DELETE'])
@login_required
def projectDelete(user):

    project_id = request.args.get('oid')

    if project_id:
        # Get a single project by ID
        project = Project.find_by_oid(ObjectId(project_id), userId=user.oid)

        if project:
            project.delete()
            return jsonify({
                'status': 'success',
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Project not found'
            }), 404
    return {'status': 'error', 'message': 'Something went wrong'}