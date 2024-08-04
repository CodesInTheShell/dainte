from flask import Blueprint, render_template, jsonify, request
from middleware import login_required

me_blueprint = Blueprint('me', __name__)


@me_blueprint.route('/api/me', methods=['GET'])
@login_required
def me(user):

    if request.method == 'GET':
        user_dict = user.to_dict()
        data = {
            "username": user.username,
            "tokenAvailable": user.tokenAvailable,
        }
        return jsonify({
            'status': 'success',
            'data': data
        })

    return {'status': 'error', 'message': 'Something went wrong'}
