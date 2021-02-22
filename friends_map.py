'''
A small web application,which creates a map,
with markers(cordinates of user's followers)
'''
from random import random,choice
from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
import folium
import requests
from geopy.exc import GeocoderUnavailable
from geopy.extra.rate_limiter import RateLimiter


geolocator = Nominatim(user_agent="friends_map.py")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.3)

app = Flask(__name__)

def get_info(surname:str,key:str) -> list:
    '''
    Sends a request to a Twitter in order to receive an
    information about user's followers.
    '''
    base_url = "https://api.twitter.com/"
    access_token = key
    search_headers = {
        'Authorization': 'Bearer {}'.format(access_token)
        }
    search_params = {
        'screen_name': surname,
        'count': 30
    }
    search_url = '{}1.1/friends/list.json'.format(base_url)
    response = requests.get(search_url,
    headers=search_headers,
    params=search_params)
    return response.json(),response.status_code

def constructor(js_str:list) -> list:
    '''
    Separates an necessary data(users loc and thier nicknames)
    from the all info.
    '''
    res = []
    friends = js_str[0]['users']
    for user in friends:
        if user['location']:
            res.append((user['location'],user['name']))
    return res

def location(data_list:list) -> list:
    '''
    Calculates the location of a place
    '''
    coords_lst = []
    count = 0
    for i in data_list:
        mist = random()
        if count == 4:
            break
        if i[0]:
            try:
                place = geolocator.geocode(i[0])
                coords = (place.latitude+mist,place.longitude+mist)
            except GeocoderUnavailable:
                continue
            except AttributeError:
                continue
            coords_lst.append((coords,i[1]))
            count += 1
    return coords_lst

def color_creator() -> str:
    '''
    Randomly chooses a color from the list.
    '''
    colors = ['darkpurple', 'black',
    'purple', 'white', 'darkgreen',
    'darkblue', 'lightgray', 'cadetblue', 'red']
    return choice(colors)

def cords_reader(data_base:list):
    '''
    Creates a coordinates map layer and returns it.
    '''
    fg_cord = folium.FeatureGroup(name='friends')
    for cord in data_base:
        fg_cord.add_child(folium.CircleMarker(
    location=[cord[0][0],cord[0][1]],
    radius = 10,popup=cord[1],color='green',
    fill_color=color_creator(),fill_opacity=1))
    return fg_cord

def map_create(friends_data:list):
    '''
    Creates a map, which also consist of the previous layer.
    '''
    mapa = folium.Map(location=[0,0],zoom_start=5)
    mapa.add_child(cords_reader(friends_data))
    mapa.save('templates/friend_map.html')

@app.route("/")
def index():
    '''
    Renders file index.html and makes it
    visible in the browser
    '''
    return render_template("index.html")


@app.route("/sent", methods=["POST"])
def register():
    '''
    The main function of the app, controls the work
    of other functions.
    '''
    name = request.form.get("name")
    token = request.form.get("token")
    if (not (token and name)) or isinstance(name,int):
        return render_template("fail.html")
    data = get_info(name,token)
    if data[1] in (401,404):
        return render_template("fail.html")
    friend_loc = location(constructor(data))
    map_create(friend_loc)
    return render_template('friend_map.html')
app.run()
