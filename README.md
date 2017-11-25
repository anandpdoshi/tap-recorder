# Dependencies

- `brew install portaudio`

```
# setup virtualenv
virtualenv --python=python3 venv
source venv/bin/activate
pip install -r requirements
mkdir temp
mkdir -p static/recordings
```

### To run the app
```
source venv/bin/activate

# For autoreload of app.py, use:
`find . -name \*.py | entr -r python app.py`

# Go to localhost:8000
```
