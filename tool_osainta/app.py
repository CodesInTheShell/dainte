from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, flash
from functools import wraps
import google.generativeai as genai
import os
import json
import jwt
import datetime
from models.users import User
from models.token_usage import TokenUsage
from views.a import a_blueprint
from views.me import me_blueprint
from views.knowledge import knowledge_blueprint
from controllers.knowledge_controller import KnowledgeController

from middleware import login_required, rate_limit, token_available_check
from osainta_core import perform_analysis, perform_general_assessment, perform_exec_sum, SYSTEM_INSTRUCTION, processAskedIrQuery


OSAINTA_SECRET_KEY = os.environ.get('OSAINTA_SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = OSAINTA_SECRET_KEY

# REGISTER BLUEPRINT VIEWS HERE
app.register_blueprint(a_blueprint)
app.register_blueprint(me_blueprint)
app.register_blueprint(knowledge_blueprint)


@app.route('/')
@login_required
def index(user):
    return render_template('index.html', user=user.to_dict())

@app.route('/icp')
@login_required
def icp(user):
    return render_template('icp.html', user=user.to_dict())

@app.route('/analyze', methods=['POST'])
@login_required
# @rate_limit
@token_available_check
def analyze(user):
    data = request.form['data']
    analysis_type = request.form.getlist('analysis_type')

    swot_analysis_result = ''
    genassess_analysis_result = ''
    exec_sum_result_obj_result = ''

    if 'SWOT' in analysis_type:
        swot_analysis_result_obj = perform_analysis('SWOT', data)
        TokenUsage.create(user.oid, swot_analysis_result_obj)
        swot_analysis_result = swot_analysis_result_obj.text

        # User AI Token Management
        user.increment_api_calls()
        user.decrementTokenAvailableBy(swot_analysis_result_obj.usage_metadata.total_token_count)
    
    if 'general_assessment' in analysis_type:
        genassess_analysis_result_obj = perform_general_assessment(data)
        TokenUsage.create(user.oid, genassess_analysis_result_obj)
        genassess_analysis_result = genassess_analysis_result_obj.text

        # User AI Token Management
        user.decrementTokenAvailableBy(genassess_analysis_result_obj.usage_metadata.total_token_count)
        user.increment_api_calls()
    
    if 'execSum' in analysis_type:
        exec_sum_result_obj = perform_exec_sum(data)
        TokenUsage.create(user.oid, exec_sum_result_obj)
        exec_sum_result_obj_result = exec_sum_result_obj.text

        # User AI Token Management
        user.decrementTokenAvailableBy(exec_sum_result_obj.usage_metadata.total_token_count)
        user.increment_api_calls()
    
    return jsonify({
        'status': 'ok', 
        'swot': swot_analysis_result, 
        'genassess': genassess_analysis_result, 
        'execSum': exec_sum_result_obj_result
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.find_by_username(username)
        if user and user.check_password(password):
            response = make_response(redirect(url_for('index')))
            access_token = jwt.encode({"sub": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)}, OSAINTA_SECRET_KEY, algorithm="HS256")
            response.set_cookie('access_token', access_token, httponly=True)
            return response
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    response = redirect(url_for('login'))
    response.delete_cookie('access_token')
    return response

@app.route('/api/askir', methods=['POST'])
@login_required
# @rate_limit
@token_available_check
def askir(user):
    data = request.get_json()

    user_query = data.get('user_query')
    context = data.get('context')

    references = KnowledgeController.getReferences(user_query, str(user.oid))
    additionalInfo = KnowledgeController.forRagInject(references)
    knowledgeNameAndChunk = KnowledgeController.kvKnowledge(references)

    model_response = processAskedIrQuery(user_query, context, ragAdditionalInfo=additionalInfo)

    response = {
            "status": "success",
            "irQuery": user_query,
            "irAnswer": model_response.text,
            "irReference": knowledgeNameAndChunk
        }
    TokenUsage.create(user.oid, model_response)
    # User AI Token Management
    user.decrementTokenAvailableBy(model_response.usage_metadata.total_token_count)
    user.increment_api_calls()
    return jsonify(response), 200

@app.route('/api/genintsum', methods=['POST'])
@login_required
# @rate_limit
@token_available_check
def genintsum(user):
    data = request.get_json()

    irs = data.get('irs')
    context = data.get('context')

    irsAnwersAndContext = ''
    for ir in irs:
        irsAnwersAndContext = '\n'+ irsAnwersAndContext + ir.get('irAnswer', '') + '\n'
    
    irsAnwersAndContext = irsAnwersAndContext + '\nCONTEXT:\n'+ context

    promptWithIrsContext = f"""
    INSTRUCTIONS:
    Your are an intillegence analyst, generate an intelligence summary following the format for the report. Analyze the given information, make use of the given information.

    INFORMATIONS:{irsAnwersAndContext}

    INTSUM FORMAT:
    Title: 
    Executive Summary: This contain the summary or your analysis. 
    Information Obtained:
    Context: 
    Assessment:
    """

    model = genai.GenerativeModel(model_name=os.environ.get('OSAINTA_MODEL', 'gemini-1.5-flash'), system_instruction=SYSTEM_INSTRUCTION)
    model_response = model.generate_content(promptWithIrsContext)

    response = {
            "status": "success",
            "intSum": model_response.text
        }
    TokenUsage.create(user.oid, model_response)
    # User AI Token Management
    user.decrementTokenAvailableBy(model_response.usage_metadata.total_token_count)
    user.increment_api_calls()
    return jsonify(response), 200
    


if __name__ == '__main__':
    if os.environ.get('OSAINTA_DEBUG'):
        app.run(debug=True)
    else:
        app.run(debug=False)