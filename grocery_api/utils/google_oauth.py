from app import app
from authlib.integrations.flask_client import OAuth
import os 

oauth = OAuth()

oauth.register('google',
    client_id = os.getenv('GOOGLE_CLIENT_ID'),
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET'),
    authorize_url = 'https://accounts.google.com/o/oauth2/auth',
    access_token_url = 'https://accounts.google.com/o/oauth2/token',
    client_kwargs = {
        'scope' : 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
        'prompt' : 'consent'
    } 
)