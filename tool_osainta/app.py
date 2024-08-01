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


OSAINTA_SECRET_KEY = os.environ.get('OSAINTA_SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = OSAINTA_SECRET_KEY
app.register_blueprint(a_blueprint)

genai.configure(api_key=os.environ.get('OSAINTA_GEMINI_API_KEY'))

SYSTEM_INSTRUCTION = """
IMPORTANT: 
Your response is in markdown.
Your name Osainta, an opensource intellligence analyst bot.
"""

def perform_analysis(analysis_type, data):
    model = genai.GenerativeModel(model_name=os.environ.get('OSAINTA_MODEL', 'gemini-1.5-flash'), system_instruction=SYSTEM_INSTRUCTION)
    prompt = f"Perform a {analysis_type} analysis on the following data:\n\n{data}"
    response = model.generate_content(prompt)
    return response

def perform_general_assessment(data):
    model = genai.GenerativeModel(model_name=os.environ.get('OSAINTA_MODEL', 'gemini-1.5-flash'), system_instruction=SYSTEM_INSTRUCTION)
    prompt = f"""Perform a general assessment analysis on the following data:\n\n{data}

    Follow the response structure below:
    Capabilities
    Vulnerabilities 
    Course of actions
    Implications to philippines
    
    """
    response = model.generate_content(prompt)
    return response

def process_ask_query(user_query, context):
    model = genai.GenerativeModel(model_name=os.environ.get('OSAINTA_MODEL', 'gemini-1.5-flash'), system_instruction=SYSTEM_INSTRUCTION)
    prompt = f"Answer the user query and be sure to refer your answer to the context if available.\n\nCONTEXT: {context}\n\nUSER QUERY: {user_query} "
    response = model.generate_content(prompt)
    return response.text

def split_text(text, chunk_size=200, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]
        chunks.append(' '.join(chunk))
        start = end - overlap
    return chunks

def embed_user_query( user_query):
    result = genai.embed_content(
            model="models/text-embedding-004",
            content=user_query,
            task_type="retrieval_document",
            title="Embedding of single string"
        )
    embedding = result['embedding']
    return embedding

def embedLargeText(large_text):
    chunks = split_text(large_text)
    chunks_and_embeddings = []

    for chunk in chunks:
        result = genai.embed_content(
                model="models/text-embedding-004",
                content=chunk,
                task_type="retrieval_document",
                title="Embedding of single string"
            )
        embedding = result['embedding']
        chunks_and_embeddings.append(
            {
                "chunk": chunk,
                "embedding": embedding
            }
        )
    return

def get_current_user():
    token = request.cookies.get('access_token')
    if not token:
        return None
    try:
        payload = jwt.decode(token, OSAINTA_SECRET_KEY, algorithms=['HS256'])
        return User.find_by_username(payload['sub'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('You need to log in first.')
            return redirect(url_for('login'))
        return f(user, *args, **kwargs)
    return decorated_function

MAX_CALLS_PER_DAY = 20

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        
        if not user.check_rate_limit(MAX_CALLS_PER_DAY):
            return jsonify({'status': 'error', 'message': 'Rate limit exceeded'}), 429
        
        return f(*args, **kwargs)
    return decorated_function

def token_available_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        
        if user.tokenAvailable < 1:
            return jsonify({'status': 'error', 'message': 'You do not have enough token'}), 429
        
        return f(*args, **kwargs)
    return decorated_function

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
@rate_limit
@token_available_check
def analyze(user):
    data = request.form['data']
    analysis_type = request.form.getlist('analysis_type')

    swot_analysis_result = ''
    genassess_analysis_result = ''

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
    
    return jsonify({'status': 'ok', 'swot': swot_analysis_result, 'genassess': genassess_analysis_result})

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
@rate_limit
@token_available_check
def askir(user):
    data = request.get_json()

    user_query = data.get('user_query')
    context = data.get('context')

    promptWithContext = f"""
    INSTRUCTIONS:
    Analyze the context and user query. Your analysis may contain any of the likelyhood expression depending if it is applicable to you analysis and be sure to apply it only on your analysis response on the question and not about the user.
    Answer the question, use the context if available for additional context.
    LIKELYHOOD OF EXPRESSION ARE: very unlikely, unlikely, likely and highly likely, almost certain.
    EXAMPLE RESPONSE: It is highly likely to rain because it is cloudy. Some other details.
    CONTEXT:\n{context}
    QUESTION: {user_query}
    """

    model = genai.GenerativeModel(model_name=os.environ.get('OSAINTA_MODEL', 'gemini-1.5-flash'), system_instruction=SYSTEM_INSTRUCTION)
    model_response = model.generate_content(promptWithContext)

    response = {
            "status": "success",
            "irQuery": user_query,
            "irAnswer": model_response.text,
            "irReference": ""
        }
    TokenUsage.create(user.oid, model_response)
    # User AI Token Management
    user.decrementTokenAvailableBy(model_response.usage_metadata.total_token_count)
    user.increment_api_calls()
    return jsonify(response), 200

@app.route('/api/genintsum', methods=['POST'])
@login_required
@rate_limit
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
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', port=5000, debug=False)