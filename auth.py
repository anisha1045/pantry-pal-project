# auth.py
from flask import Flask, redirect, request, session
from requests_oauthlib import OAuth2Session
import os
import threading
import webbrowser

# Flask setup
app = Flask(__name__)
app.secret_key = os.urandom(24)

# OAuth2 config
client_id = "1157250652-tmr0ju9g9a3rb0vosg3r3v9ipi45hv86.apps.googleusercontent.com"
client_secret = "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"
redirect_uri = "http://localhost:5000/callback"

authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"
userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"

# shared state
user_email = None

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login")
def login():
    google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=["profile", "email"])
    auth_url, state = google.authorization_url(
        authorization_base_url,
        access_type="offline", prompt="select_account"
    )
    session['oauth_state'] = state
    return redirect(auth_url)

@app.route("/callback")
def callback():
    global user_email
    google = OAuth2Session(client_id, redirect_uri=redirect_uri, state=session['oauth_state'])
    token = google.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)
    google = OAuth2Session(client_id, token=token)
    userinfo = google.get(userinfo_url).json()

    email = userinfo.get("email")
    session['username'] = email
    user_email = email

    # Save to file for terminal use
    with open("logged_in_user.txt", "w") as f:
        f.write(email)

    return f"<h2>Login successful!</h2><p>You can now return to the Pantry Pal terminal app.</p>"

def login_with_google():
    def run_app():
        app.run(port=5000, debug=False)

    # Start Flask in background
    thread = threading.Thread(target=run_app)
    thread.daemon = True
    thread.start()

    # Open browser for user to sign in
    webbrowser.open("http://localhost:5000", new=1)

    # Wait until user_email is set via callback
    import time
    global user_email
    while user_email is None:
        time.sleep(1)

    return user_email
