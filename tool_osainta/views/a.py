from flask import Blueprint, render_template
from middleware import login_required

a_blueprint = Blueprint('a', __name__)

@a_blueprint.route('/a', defaults={'path': ''})
@a_blueprint.route('/a/<path:path>')  
@login_required
def a(user, path):
    return render_template('a.html')