from flask import Flask, Response, request, redirect
from PIL import Image, ImageDraw, ImageFont
import io
import time
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "fonts")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Global variables to store the latest image and timestamp
latest_image = None
last_image_time = 0

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
    global latest_image, last_image_time
    image_file = request.files.get("image")
    if image_file:
        image = Image.open(image_file)
        latest_image = image.copy()  # Copy the image to ensure it's in memory
        last_image_time = time.time()  # Update the timestamp
    return "Image uploaded", 200

@app.route("/stream.mjpg")
def stream():
    def generate():
        while True:
            current_time = time.time()
            if latest_image and (current_time - last_image_time <= TIMEOUT):
                buf = io.BytesIO()
                latest_image.save(buf, format='JPEG')
                frame = buf.getvalue()
            else:
                buf = io.BytesIO()
                default_image.save(buf, format='JPEG')
                frame = buf.getvalue()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(1)  # Small delay to control frame rate

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/index.html")
def index():
    return open(os.path.join(TEMPLATES_DIR, "stream.html")).read()

@app.route("/")
def home():
    return redirect("/index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)