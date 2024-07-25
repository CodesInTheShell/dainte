from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

SYSTEM_INSTRUCTION = "Repond in html format inside a <div> tag."


def swot_analysis(analysis_type, api_key, data):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_INSTRUCTION)
    prompt = f"Perform a {analysis_type} analysis on the following data:\n\n{data} and IMPORTANT: Repond in html format inside a <div> tag."
    response = model.generate_content(prompt)
    return response.text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    api_key = request.form['api_key']
    data = request.form['data']
    analysis_type = request.form.getlist('analysis_type')

    # For now, we only process SWOT analysis
    if 'SWOT' in analysis_type:
        analysis_result = swot_analysis(analysis_type, api_key, data)
        return jsonify({'status': 'ok', 'swot': analysis_result})
    else:
        return jsonify({'status': 'error', 'message': 'Unsupported analysis type'})

if __name__ == '__main__':
    app.run(debug=True)