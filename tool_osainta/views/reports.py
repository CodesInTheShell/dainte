from flask import Blueprint, render_template, jsonify, request
from middleware import login_required, rate_limit
from models.report import Report
from bson.objectid import ObjectId

import json
import datetime

report_blueprint = Blueprint('report', __name__)


@report_blueprint.route('/api/report', methods=['GET'])
@login_required
def report(user):
    report_id = request.args.get('id')

    if report_id:
        # Get a single report by ID
        report = Report.find_by_oid(ObjectId(report_id), userId=user.oid)

        if report:
            report_dict = report.to_dict()
            data = {
                "name": report.name,
                "content": report.content,
                "oid": str(report.oid),
                "userId": str(report.userId),
                "created": report.created.isoformat() if report.created else None , 
                "projectId": str(report.projectId),
            }
            return jsonify({
                'status': 'success',
                'data': data
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Report not found'
            }), 404
    return {'status': 'error', 'message': 'Something went wrong'}
        


@report_blueprint.route('/api/report-list', methods=['GET'])
@login_required
def list_reports(user):
    # Get all reports
    projectId = request.args.get('projectId', None)

    if projectId:
        reports = Report.find_all(projectId=projectId, userId=user.oid)
    else:
        reports = Report.find_all(userId=user.oid)


    report_list = []

    for report in reports:
        pData = {
            "name": report.name,
            "content": report.content,
            "created": report.created.isoformat(),
            "oid": str(report.oid),
            "userId": str(report.userId),
            "projectId": str(report.projectId),
        }
        report_list.append(pData)

    if report_list:
        return jsonify({
            'status': 'success',
            'data': report_list
        })

    return {'status': 'success', 'data': report_list}

@report_blueprint.route('/api/report', methods=['POST'])
@login_required
@rate_limit
def reportPost(user):
    
    data = request.get_json()

    reportName = data.get('reportName')
    reportContent = data.get('reportContent')
    reportProjectId = data.get('reportProjectId')


    report = Report.from_dict({
        "name": reportName,
        "content": reportContent,
        "userId": user.oid,
        "projectId": ObjectId(reportProjectId),
        "created": datetime.datetime.now(),
    })
    report.save()

    report = Report.find_by_oid(ObjectId(report.oid), userId=user.oid)
    data = {
        "name": report.name,
        "content": report.content,
        "projectId": str(report.projectId),
        "userId": str(report.userId),
        "created": report.created.isoformat(),
        "oid": str(report.oid)
    }
    
    return jsonify({
        'status': 'success',
        'data': data
    })


@report_blueprint.route('/api/report-delete', methods=['DELETE'])
@login_required
def reportDelete(user):

    report_id = request.args.get('oid')

    if report_id:
        # Get a single report by ID
        report = Report.find_by_oid(ObjectId(report_id), userId=user.oid)

        if report:
            report.delete()
            return jsonify({
                'status': 'success',
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Report not found'
            }), 404
    return {'status': 'error', 'message': 'Something went wrong'}