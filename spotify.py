from flask import Flask, redirect, request, session, url_for, render_template
import requests

app = Flask(__name__)
app.secret_key = 'temp'

# Spotify API credentials
CLIENT_ID = '{your client id}'
CLIENT_SECRET = '{your client secret}'
REDIRECT_URI = 'http://localhost:8000/callback'

# Spotify API endpoints
SPOTIFY_API_URL = 'https://api.spotify.com/v1'
AUTH_URL = 'https://accounts.spotify.com/authorize'

@app.get('/')
def index():
    if 'access_token' in session:
        return redirect(url_for('top_tracks'))
    else:
        return '<a href="/login">Login with Spotify</a>'

@app.get('/login')
def login():
    payload = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'user-top-read',
    }

    # Create an empty list to store key-value pairs in the format "key=value"
    query_parameters = []

    # Iterate over each key-value pair in the payload dictionary
    for key, value in payload.items():
        # Format the key-value pair as "key=value" and add it to the list
        query_parameters.append(f"{key}={value}")

    # Join all key-value pairs with '&' and append them to the AUTH_URL
    redirect_url = AUTH_URL + '?' + '&'.join(query_parameters)

    # Redirect the user to the constructed URL
    return redirect(redirect_url)


@app.get('/callback')
def callback():
    code = request.args.get('code')
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    response = requests.post('https://accounts.spotify.com/api/token', data=payload)
    access_token = response.json()['access_token']
    session['access_token'] = access_token
    return redirect(url_for('top_tracks'))

@app.get('/top-tracks')
def top_tracks():
    if 'access_token' not in session:
        return redirect(url_for('login'))

    headers = {'Authorization': f"Bearer {session['access_token']}"}
    response = requests.get(f"{SPOTIFY_API_URL}/me/top/tracks?limit=50", headers=headers)
    tracks = response.json()['items']

    return render_template('top_tracks.html', tracks=tracks)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)