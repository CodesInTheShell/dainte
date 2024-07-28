from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, flash
from functools import wraps
import google.generativeai as genai
import os
import json
import jwt
import datetime

OSAINTA_SECRET_KEY = os.environ.get('OSAINTA_SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = OSAINTA_SECRET_KEY

genai.configure(api_key=os.environ.get('OSAINTA_GEMINI_API_KEY'))

SYSTEM_INSTRUCTION = "IMPORTANT: Your response is in html format inside a <div> tag."

def swot_analysis(analysis_type, data):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_INSTRUCTION)
    prompt = f"Perform a {analysis_type} analysis on the following data:\n\n{data} and IMPORTANT: Respond in html format inside a <div> tag."
    response = model.generate_content(prompt)
    return response.text

def process_ask_query(user_query, context):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_INSTRUCTION)
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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            flash('You need to log in first.')
            return redirect(url_for('login'))
        try:
            jwt.decode(token, OSAINTA_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            flash('Session expired, please log in again.')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Invalid token, please log in.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/icp')
@login_required
def icp():
    return render_template('icp.html')

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.form['data']
    analysis_type = request.form.getlist('analysis_type')

    if 'SWOT' in analysis_type:
        analysis_result = swot_analysis(analysis_type, data)
        return jsonify({'status': 'ok', 'swot': analysis_result})
    else:
        return jsonify({'status': 'error', 'message': 'Unsupported analysis type'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_string = os.environ.get('OSAINTA_USER')  # '{"someuser": "somepassword"}'
        if user_string:
            user_object = json.loads(user_string)

            if username in user_object.keys() and password == user_object.get(username):
                response = make_response(redirect(url_for('index')))
                access_token = jwt.encode({"sub": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)}, OSAINTA_SECRET_KEY, algorithm="HS256")
                response.set_cookie('access_token', access_token, httponly=True, secure=True)
                return response
            return render_template('login.html', error='Invalid username or password')
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    response = redirect(url_for('login'))
    response.delete_cookie('access_token')
    return response

if __name__ == '__main__':
    if os.environ.get('OSAINTA_DEBUG'):
        app.run(debug=True)
    else:
        app.run(debug=False)