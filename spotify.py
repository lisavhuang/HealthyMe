#refers to https://github.com/drshrey/spotify-flask-auth-example
import json
from urllib.parse import quote
import requests
# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.



#  Client Keys
#Can get one from making an account on the spotify devlelopers website
CLIENT_ID = ""
CLIENT_SECRET = ""

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
#insert your own server url
CLIENT_SIDE_URL = ""
PORT = 5000
REDIRECT_URI = "{}:{}/callback".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
	"response_type": "code",
	"redirect_uri": REDIRECT_URI,
	"scope": SCOPE,
	# "state": STATE,
	# "show_dialog": SHOW_DIALOG_str,
	"client_id": CLIENT_ID
}
def index():
	# Auth Step 1: Authorization
	url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
	auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
	return auth_url


def callback(auth_token):
	# Auth Step 4: Requests refresh and access tokens
	code_payload = {
	"grant_type": "authorization_code",
	"code": str(auth_token),
	"redirect_uri": REDIRECT_URI,
	'client_id': CLIENT_ID,
	'client_secret': CLIENT_SECRET,
	}
	post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

	# Auth Step 5: Tokens are Returned to Application
	response_data = json.loads(post_request.text)
	access_token = response_data["access_token"]
	refresh_token = response_data["refresh_token"]
	token_type = response_data["token_type"]
	expires_in = response_data["expires_in"]

	# Auth Step 6: Use the access token to access Spotify API
	auth_header = {"Authorization": "Bearer {}".format(access_token)}
	return auth_header	

def get_bpm_playlists(bpm,auth_header):
	playlist_api_endpoint = "{}/search?q=%22{}%22&type=playlist".format(SPOTIFY_API_URL,bpm)
	playlists_response = requests.get(playlist_api_endpoint, headers = auth_header)
	playlists_data = json.loads(playlists_response.text)
	return playlists_data

