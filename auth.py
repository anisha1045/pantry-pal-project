# auth.py
from flask import Blueprint, redirect, request, session, url_for
from requests_oauthlib import OAuth2Session
from db import user_in_db, add_new_user
from db_conn import conn
import os
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
auth_bp = Blueprint('auth', __name__)

# OAuth2 config
client_id = "1157250652-tmr0ju9g9a3rb0vosg3r3v9ipi45hv86.apps.googleusercontent.com"
client_secret = "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"
redirect_uri = "https://pantrypal.pythonanywhere.com/auth/callback"
#redirect_uri = "http://127.0.0.1:5000/auth/callback"
#redirect_uri = "http://localhost:5000/auth/callback"
#redirect_uri = "http://localhost:5000/callback"



authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"
userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"

@auth_bp.route("/google")
def login():
    google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=["profile", "email"])
    auth_url, state = google.authorization_url(authorization_base_url, access_type="offline", prompt="select_account")
    session['oauth_state'] = state
    return redirect(auth_url)

@auth_bp.route("/callback")
def callback():
    try: 
        google = OAuth2Session(
            client_id, redirect_uri=redirect_uri, state=session['oauth_state'])
        token = google.fetch_token(
            token_url, client_secret=client_secret, authorization_response=request.url)
        google = OAuth2Session(client_id, token=token)
        userinfo = google.get(userinfo_url).json()

        email = userinfo.get("email")
        session['username'] = email   

        if not user_in_db(conn, email):
            # Add user with empty/default profile fields
            print("Adding new user: ", email)
            add_new_user(conn, email, '', '', '', '', '', '', '')
            print("Added successfully.")

        return redirect(url_for("one_time_setup"))

    except Exception as e:
        return f"Google OAuth failed: {str(e)}", 500

    



