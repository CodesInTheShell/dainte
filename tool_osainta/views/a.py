from flask import Blueprint, render_template

a_blueprint = Blueprint('a', __name__)

@a_blueprint.route('/a', defaults={'path': ''})
@a_blueprint.route('/a/<path:path>')  
def a(path):
    return render_template('a.html')