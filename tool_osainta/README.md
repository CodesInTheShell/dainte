Be sure you have a gemini api key
Be sure you have python installed, virtualenv is recommended.
Be sure you have pip install -r requirements.txt
Be sure you are inside tool_osainta directory

# Running the app
export OSAINTA_USER='{"someuser": "somepassword"}'
export OSAINTA_SECRET_KEY='someverybestofallkindofyoursecretkeyherchangeasneeded'
export OSAINTA_GEMINI_API_KEY='yougeminiapikeyhere'
export OSAINTA_DEBUG=1
python app.py