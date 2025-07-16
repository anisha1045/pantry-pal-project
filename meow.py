from flask import Flask, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/')
def index():
    session['username'] = 'anisha'
    return 'Session set!'

if __name__ == '__main__':
    app.run(debug=True)