import requests
import json

# Replace this with your actual Google API key
GOOGLE_API_KEY = 'your_google_api_key_here'

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
headers = {
    'Content-Type': 'application/json'
}
data = {
    "contents": [{
        "parts": [{
            "text": "Write a story about a magic backpack."
        }]
    }]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
    print("Response JSON:", response.json())
else:
    print(f"Request failed with status code {response.status_code}")
    print("Response content:", response.content)

class GemApi:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"


    def generate_content(self, data):
        """
        data = { 
                    "system_instruction": {
                    "parts":
                        { 
                            "text": "You are Neko the cat respond like one"
                        }
                    },
                    "contents": {
                    "parts": {
                        "text": "Hello there"
                        }
                    }
                }
        """
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Request generate_content failed with status code {response.status_code}")
    

