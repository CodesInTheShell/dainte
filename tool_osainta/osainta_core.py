import google.generativeai as genai
import os



genai.configure(api_key=os.environ.get('OSAINTA_GEMINI_API_KEY'))


# SYSTEM_INSTRUCTION = """
# IMPORTANT: 
# Your response is in markdown.
# Your name Osainta, an opensource intellligence analyst bot.

# You adhere to the ICD-203 guidelines. Your responses should reflect the following principles:

# 1. **Objectivity**: Perform analysis with objectivity, considering all relevant perspectives, and mitigating biases.
# 2. **Political Independence**: Ensure that your assessments are free from political influence and advocacy.
# 3. **Actionable**: Provide actionable analysis.
# 5. **Analytic Tradecraft Standards**:
#    - Express and explain uncertainties in analytic judgments, using consistent likelihood terms (e.g., very unlikely, likely, nearly certain).
#    - Distinguish between underlying intelligence information, assumptions, and judgments.
#    - Consider and assess plausible alternative hypotheses.
#    - Present clear and logical arguments, supporting judgments with coherent reasoning.
#    - Explain how judgments have changed or remained consistent with previous analysis.
#    - Strive for accuracy, reducing ambiguity by clearly expressing the likelihood, timing, and nature of outcomes.
# """

SYSTEM_INSTRUCTION = """
IMPORTANT: 
Your response is in markdown.
Your name Osainta, an opensource intellligence analyst bot.
You adhere to the ICD-203 guidelines. 
"""
# Perform analysis with objectivity, considering all relevant perspectives, and mitigating biases. Ensure that your assessments are free from political influence and advocacy, your analysis should be actionable, you express and explain uncertainties in analytic judgments using consistent likelihood terms (e.g., very unlikely, unlikely, likely, highly likely, nearly certain), you should be able to distinguish between underlying intelligence information, assumptions, and judgments, you should consider and assess plausible alternative hypotheses, your analysis should present clear and logical arguments, supporting judgments with coherent reasoning, reducing ambiguity by clearly expressing the likelihood, timing, and nature of outcomes.


OSAINTA_EMBEDDING_MODEL = os.environ.get('OSAINTA_EMBEDDING_MODEL', 'models/text-embedding-004')


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

def perform_exec_sum(data):
    model = genai.GenerativeModel(model_name=os.environ.get('OSAINTA_MODEL', 'gemini-1.5-flash'), system_instruction=SYSTEM_INSTRUCTION)
    prompt = f"""Analyze then generate an executive summary based on the following data. 
    Your assessment may contain any of the likelyhood expression depending if it is applicable.
    LIKELYHOOD FOR ASSESSMENT: very unlikely, unlikely, likely and highly likely, almost certain.
    EXAMPLE RESPONSE: It is highly likely to rain because it is cloudy. Some other details.
    DATA:\n{data}
    """
    response = model.generate_content(prompt)
    return response

def process_ask_query(user_query, context):
    model = genai.GenerativeModel(model_name=os.environ.get('OSAINTA_MODEL', 'gemini-1.5-flash'), system_instruction=SYSTEM_INSTRUCTION)
    prompt = f"Answer the user query and be sure to refer your answer to the context if available.\n\nCONTEXT: {context}\n\n {additionalInfo}\n\nUSER QUERY: {user_query} "
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
            model=OSAINTA_EMBEDDING_MODEL,
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
                model=OSAINTA_EMBEDDING_MODEL,
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

def processAskedIrQuery(user_query, context, ragAdditionalInfo=''):

    promptWithContext = f"""
    INSTRUCTIONS:
    Understand the context, additional information and the user question.
    Answer the question, use the context and additional information if available for additional context.
    \n{ragAdditionalInfo}\n
    CONTEXT:\n{context}
    QUESTION: {user_query}
    """
    model = genai.GenerativeModel(model_name=os.environ.get('OSAINTA_MODEL', 'gemini-1.5-flash'), system_instruction=SYSTEM_INSTRUCTION)
    model_response = model.generate_content(promptWithContext)

    return model_response


import typing_extensions as typing

class SearchLinks(typing.TypedDict):
  search_link: str

def generateSuggestedLinks(data):
    promptWithContext = f"""
    Generate a suggestion google search links regarding the following information I want to do research. Give me a 5 google search link the would likely lead to a better result. Respond in the format of {{'data': [ 'https://www.google.com/search?q=sam_wincester']}}
    
    example link:
    https://www.google.com/search?q=sam_wincester

    Information:
    {data.get('projectName', '')}. {data.get('projectDescription', '')}
    """
    model = genai.GenerativeModel(
        model_name=os.environ.get('OSAINTA_MODEL', 'gemini-1.5-flash'), 
        system_instruction=SYSTEM_INSTRUCTION,
        generation_config={"response_mime_type": "application/json", "response_schema": list[SearchLinks]}
        )
    model_response = model.generate_content(promptWithContext)

    return model_response
    