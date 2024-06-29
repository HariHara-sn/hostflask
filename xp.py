'''The below code have only 4 requests '''
# from flask import Flask, request, render_template_string
# from geopy.geocoders import Nominatim
# import folium

# app = Flask(__name__)

# def get_address(lat, lon):
#     geolocator = Nominatim(user_agent="geoapiExercises")
#     location = geolocator.reverse((lat, lon))
#     return location.address

# def create_map(lat, lon):
#     location_map = folium.Map(location=[lat, lon], zoom_start=15)
#     folium.Marker([lat, lon], popup=get_address(lat, lon)).add_to(location_map)
#     return location_map._repr_html_()  # Returns the HTML representation of the map

# @app.route('/')
# def index():
#     return render_template_string('''
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>Get Current Location</title>
#         </head>
#         <body>
#             <h1>Get Device Coordinates</h1>
#             <button onclick="getLocation()">Get Location</button>
#             <div id="map"></div>
#             <p id="demo"></p>
#             <script>
#                 function getLocation() {
#                     if (navigator.geolocation) {
#                         navigator.geolocation.getCurrentPosition(showPosition);
#                     } else {
#                         document.getElementById("demo").innerHTML = "Geolocation is not supported by this browser.";
#                     }
#                 }

#                 function showPosition(position) {
#                     const lat = position.coords.latitude;
#                     const lon = position.coords.longitude;
#                     document.getElementById("demo").innerHTML = "Latitude: " + lat + "<br>Longitude: " + lon;

#                     // Send data to server
#                     fetch(`/location?lat=${lat}&lon=${lon}`)
#                         .then(response => response.text())
#                         .then(data => {
#                             document.getElementById("map").innerHTML = data;
#                         });
#                 }
#             </script>
#         </body>
#         </html>
#     ''')

# @app.route('/location')
# def location():
#     lat = float(request.args.get('lat'))
#     lon = float(request.args.get('lon'))
#     location_map_html = create_map(lat, lon)
#     return location_map_html

# if __name__ == '__main__':
#     app.run(debug=True)


''' The below is code is add a api '''
from flask import Flask, request, render_template_string, jsonify
from opencage.geocoder import OpenCageGeocode
import folium
import math

app = Flask(__name__)

opencage_api_key = 'd0912921b03b43ef94bf5cccb2194195'
geocoder = OpenCageGeocode(opencage_api_key)

# Store coordinates for two devices
device_coordinates = {}

def get_address(lat, lon):
    results = geocoder.reverse_geocode(lat, lon)
    if results and len(results):
        return results[0]['formatted']
    return "Address not found"

def create_map(lat, lon):
    location_map = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker([lat, lon], popup=get_address(lat, lon)).add_to(location_map)
    return location_map._repr_html_()  # Returns the HTML representation of the map

def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Get Current Location</title>
        </head>
        <body>
            <h1>Get Device Coordinates</h1>
            <button onclick="getLocation('device1')">Get Location for Device 1</button>
            <button onclick="getLocation('device2')">Get Location for Device 2</button>
            <div id="map"></div>
            <p id="demo"></p>
            <p id="distance"></p>
            <script>
                function getLocation(device) {
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition((position) => showPosition(position, device));
                    } else {
                        document.getElementById("demo").innerHTML = "Geolocation is not supported by this browser.";
                    }
                }

                function showPosition(position, device) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    document.getElementById("demo").innerHTML = "Latitude: " + lat + "<br>Longitude: " + lon;

                    // Send data to server
                    fetch(`/location?lat=${lat}&lon=${lon}&device=${device}`)
                        .then(response => response.text())
                        .then(data => {
                            document.getElementById("map").innerHTML = data;
                            if (device === 'device2') {
                                fetch('/distance')
                                    .then(response => response.json())
                                    .then(data => {
                                        document.getElementById("distance").innerHTML = "Distance between devices: " + data.distance + " km";
                                    });
                            }
                        });
                }
            </script>
        </body>
        </html>
    ''')

@app.route('/location')
def location():
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    device = request.args.get('device')

    device_coordinates[device] = (lat, lon)
    
    location_map_html = create_map(lat, lon)
    return location_map_html

@app.route('/distance')
def distance():
    if 'device1' in device_coordinates and 'device2' in device_coordinates:
        lat1, lon1 = device_coordinates['device1']
        lat2, lon2 = device_coordinates['device2']
        distance_km = haversine(lat1, lon1, lat2, lon2)
        return jsonify({"distance": distance_km})
    else:
        return jsonify({"error": "Both devices need to send their location first."})

if __name__ == '__main__':
    app.run(debug=True)
