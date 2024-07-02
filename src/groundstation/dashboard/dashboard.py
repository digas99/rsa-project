import base64
from flask import Flask, Response, request, redirect, jsonify, render_template
from PIL import Image, ImageDraw, ImageFont
import io
import time
import os
import sys
import requests
import threading

from sqlalchemy import create_engine
from sqlalchemy.engine import reflection
from db_config import *
from models import *

import mysql.connector
from mysql.connector import Error

from dotenv import load_dotenv
load_dotenv()

TILE_URL = os.getenv("TILE_URL")

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mission.geometry import PolygonDivision 
from mission.mission import Missions

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "fonts")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app.config['SQLALCHEMY_DATABASE_URI'] = get_db()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = get_sqlalchemy_track_modifications()

db.init_app(app)

with app.app_context():
    engine = create_engine(get_db())
    inspector = reflection.Inspector.from_engine(engine)
    tables = inspector.get_table_names()
    if not "mission" in tables:
        print(" * Creating tables...")
        db.create_all()

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Global variables to store the latest image and timestamp
latest_image_device1 = None
last_image_time1 = 0
latest_image_device2 = None
last_image_time2 = 0

def make_frame(text):
    # Create a new image
    default_image = Image.new('RGB', (640, 480), color = (73, 109, 137))
    d = ImageDraw.Draw(default_image)

    # Increase font size (adjust as needed)
    font_size = 40

    # Set font using default Pillow font (adjust size)
    d.font = ImageFont.truetype(font=os.path.join(FONT_DIR, "arial.ttf"), size=font_size)

    # Get text width using textlength
    text_width = d.textlength(text)

    # Estimate text height based on new font size
    estimated_text_height = d.font.size * 1.2

    # Calculate center coordinates
    center_x = (default_image.width - text_width) // 2
    center_y = (default_image.height - estimated_text_height) // 2

    # Draw the text with centered coordinates
    d.text((center_x, center_y), text, fill=(255,255,0))
    return default_image

default_image = make_frame("Not receiving frames")

TIMEOUT = 10  # seconds

@app.route("/upload", methods=["POST"])
def upload():
    global latest_image_device1, last_image_time_device1
    global latest_image_device2, last_image_time_device2

    device = request.args.get("device")  # Get the device parameter from the URL
    image_file = request.files.get("image")
    
    if not device or device not in ["device1", "device2"]:
        return "Invalid or missing device parameter", 400

    if image_file:
        image = Image.open(image_file)
        if device == "device1":
            latest_image_device1 = image.copy()
            last_image_time_device1 = time.time()
        elif device == "device2":
            latest_image_device2 = image.copy()
            last_image_time_device2 = time.time()
    
    return "Image uploaded", 200


@app.route("/stream.mjpg")
def stream():
    device = request.args.get("device")  # Get the device parameter from the URL
    def generate(device):
        if not device or device not in ["device1", "device2"]:
            return "Invalid or missing device parameter", 400
        
        while True:
            current_time = time.time()
            if device == "device1" and latest_image_device1 and (current_time - last_image_time_device1 <= TIMEOUT):
                image = latest_image_device1
            elif device == "device2" and latest_image_device2 and (current_time - last_image_time_device2 <= TIMEOUT):
                image = latest_image_device2
            else:
                # Load default image if no valid image is available
                image = default_image.copy()
            
            buf = io.BytesIO()
            image.save(buf, format='JPEG')
            frame = buf.getvalue()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(1)  # Small delay to control frame rate

    return Response(generate(device), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/generate", methods=["POST"])
def generate():
    body = request.get_json()
    coordinates = body.get("coordinates")

    division = PolygonDivision(coordinates)
    division.split(point_index=1)
    division.resize(scale=0.8)
    division.print()

    plot_path = division.plot(show=False)
    polygons = division.polygons()

    missions = Missions(
        drones=body.get("drones"),
        polygons=division.split_polygons,
        options={
            'alt': 3,
            'speed': 3,
            'save_path': 'missions',
            'close_loop': True
        }
    )

    missions.generate()
    files = missions.save()

	# save missions to database
    for mission in files:
        store_mission(mission)

    image = Image.open(plot_path)

    if image.mode == 'RGBA':
        image = image.convert('RGB')

    buf = io.BytesIO()
    image.save(buf, format='JPEG')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")

    response = {
        "polygons": polygons,
        "image": img_base64,
        "center": division.centroid.coords[0],
        "missions": files,
    }

    return jsonify(response)

def store_mission(mission):
    mission_file = MissionFile.query.filter_by(file=mission.get("file")).first()

    if mission_file:
        db.session.delete(mission_file)
        db.session.commit()

    mission_file = MissionFile(
        file=mission.get("file"),
    )
    db.session.add(mission_file)
    db.session.commit()

    center = MissionCoords(
        mission_file=mission_file.id,
        lat=mission.get("polygon").get("center")[0],
        lon=mission.get("polygon").get("center")[1]
    )
    db.session.add(center)
    db.session.commit()

    mission_file.center = center.id
    db.session.commit()

    for coord in mission.get("polygon").get("coords"):
        coords = MissionCoords(
            mission_file=mission_file.id,
            lat=coord[0],
            lon=coord[1]
        )
        db.session.add(coords)
    db.session.commit()


@app.route("/station", methods=["POST"])
def station():
    body = request.get_json()
    station_url = body.get("station")
    print(station_url)
    drones = body.get("drones")
    if station_url:
        url = f"{station_url}/drone?data=info"
        headers = {
            "Accept": "application/json"
        }

        print(f"Requesting drones from station: {url}")
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                station_drones = data
                droneIds = [drone['droneId'] for drone in station_drones if drone['state'] == 'ready']
                drones = [drone for drone in drones if drone in droneIds]

                return jsonify(drones)  # Return the drones that are available in the station            
        except Exception as e:
            print(f"Failed to connect to the station: {e}")
            pass

    # Return an error message if the request to the station failed
    return jsonify({"error": "Failed to connect to the station"}), 500


@app.route("/mission", methods=["POST"])
def mission():
    body = request.get_json()
    station_url = body.get("station")
    drones = body.get("drones")

    if station_url:
        url = f"{station_url}/mission"
        headers = {
            "Accept": "application/json",
        }

        for info in drones:
            drone = info.get("name")

            mission_file = f"{drone}_mission.groovy"
            mission_path = os.path.join("missions", mission_file)
            
            # send the binary file
            try:
                with open(mission_path, "rb") as f:
                    binary_data = f.read()
                    response = requests.post(url, data=binary_data, headers=headers)
                    mission_id = response.json().get("missionId")


                    mission = Mission.query.filter_by(drone_id=drone).first()

                    mission_file = MissionFile.query.filter_by(file=mission_file).first()
                    if mission_file:                        
                        if not mission:
                            mission = Mission(
                                groundstation=station_url,
                                drone_id=drone,
                                drone_server=info.get("server"),
                                mission_id=mission_id,
                                mission_file=mission_file.id
                            )
                            db.session.add(mission)
                        else:
                            mission.groundstation = station_url
                            mission.mission_id = mission_id
                            mission.mission_file = mission_file.id

                        db.session.commit()

            except Exception as e:
                print(f"Failed to send mission to drone {drone}: {e}")
                pass

            # force a 500ms delay between each request
            time.sleep(0.5)

        return jsonify({"message": "Missions sent to drones"})
    else:
        return jsonify({"error": "Station URL is required"}), 400


@app.route("/avoidance/<drone>", methods=["POST"])
def avoidance(drone):
    mission = Mission.query.filter_by(drone_id=drone).first()

    if not mission:
        return jsonify({"error": "Mission not found"}), 404
    
    if mission.paused:
        return jsonify({"message": "Mission paused"}), 400

    # Call avoid on a new thread
    thread = threading.Thread(target=avoid, args=(drone,))
    thread.start()

    return jsonify({"message": "Avoidance ended"}), 200


def avoid(drone):
    with app.app_context():
        mission = Mission.query.filter_by(drone_id=drone).first()
        station_url = mission.groundstation
        mission_id = mission.mission_id

        if station_url and mission_id:
            url = f"{station_url}/mission/{mission_id}/pause"
            headers = {
                "Accept": "application/json",
            }

            try:
                response = requests.post(url, headers=headers)

                if response.status_code == 200:
                    print(f"Mission paused for drone {drone}")

                    # update state of mission to paused
                    mission.paused = True
                    db.session.commit()

                    # build avoidance
                    mission_info = MissionFile.query.filter_by(id=mission.mission_file).first()
                    center = MissionCoords.query.filter_by(id=mission_info.center).first()

                    # go to center
                    goto = {
                        "mode": "action",
                        "cmd": "goto",
                        "lat": center.lat,
                        "lon": center.lon
                    }

                    url = f"{station_url}/drone/{drone}/cmd"
                    try:
                        response = requests.post(url, json=goto, headers=headers)

                        if response.status_code == 200:
                            print(f"Drone {drone} going to center")
                    except Exception as e:
                        print(f"Failed to send goto command to drone {drone}: {e}")
                        pass

                    avoidance_time = 3
                    time.sleep(avoidance_time)

                    # cancel command
                    cancel = {
                        "mode": "custom",
                        "cmd": "cancel"
                    }

                    try:
                        response = requests.post(url, json=cancel, headers=headers)

                        if response.status_code == 200:
                            print(f"Drone {drone} mission cancelled")
                    except Exception as e:
                        print(f"Failed to cancel mission for drone {drone}: {e}")
                        pass

                    time.sleep(1)

                    # resume mission
                    url = f"{station_url}/mission/{mission_id}/resume"
                    resume = {
                        "action": "start_next"
                    }
                    try:
                        response = requests.post(url, json=resume, headers=headers)

                        if response.status_code == 200:
                            print(f"Mission resumed for drone {drone}")

                            # update state of mission to resumed
                            mission.paused = False
                            db.session.commit()

                            # resume avoidance on the drone
                            url = f'{mission.drone_server}/reset'

                            try:
                                response = requests.post(url, headers=headers)

                                if response.status_code == 200:
                                    print(f"Avoidance for drone {drone} resumed")
                            except Exception as e:
                                print(f"Failed to resume avoidance for drone {drone}: {e}")
                                pass
                                
                            return jsonify({"message": "Mission resumed"})
                    except Exception as e:
                        print(f"Failed to resume mission for drone {drone}: {e}")
                        pass

                    return jsonify({"message": "Collision avoided"})
            except Exception as e:
                print(f"Failed to pause mission for drone {drone}: {e}")
                pass

            return jsonify({"error": "Mission ID not found"}), 404
        else:
            return jsonify({"error": "No station recorded yet"}), 400


@app.route("/index.html")
def index():
    return render_template("mission.html", tile_url=TILE_URL)

@app.route("/")
def home():
    return redirect("/index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
