import argparse
import cv2
import os
import socketserver
import threading
import logging
import numpy as np
import piexif

from http import server
from picamera2 import Picamera2
from detection import Detector

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PAGE = """\
<html>
<head>
<title>picamera2 MJPEG streaming demo</title>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

output = None

class StreamingHandler(server.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/':
			self.send_response(301)
			self.send_header('Location', '/index.html')
			self.end_headers()
		elif self.path == '/index.html':
			content = PAGE.encode('utf-8')
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.send_header('Content-Length', len(content))
			self.end_headers()
			self.wfile.write(content)
		elif self.path == '/stream.mjpg':
			self.send_response(200)
			self.send_header('Age', 0)
			self.send_header('Cache-Control', 'no-cache, private')
			self.send_header('Pragma', 'no-cache')
			self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
			self.end_headers()
			try:
				while True:
					if output is None:
						continue

					frame = output
					self.wfile.write(b'--FRAME\r\n')
					self.send_header('Content-Type', 'image/jpeg')
					self.send_header('Content-Length', len(frame))
					self.end_headers()
					self.wfile.write(frame)
					self.wfile.write(b'\r\n')
			except ConnectionResetError:
				logging.warning('Connection reset by client')
			except Exception as e:
			    logging.warning(
								'Removed streaming client %s: %s',
								self.client_address, str(e))
		else:
			self.send_error(404)
			self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def handle_image(people, frame, _):
	print(f"People detected: {people}")

	output_dir = os.path.join(BASE_DIR, "../output")
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	
	num_files = len(os.listdir(output_dir))
	cv2.imwrite(f"{output_dir}/output{num_files}.jpg", frame)

def handle_stream(people, frame, image):
	print(f"People detected: {people}")
	global output
	output = image

def start_server():
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()

def main():
	# handle command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument('-i', '--image', required=False,
					help = 'path to input image')
	
	args = ap.parse_args()
	
	detector = Detector()
	
	if args.image:
		image = cv2.imread(args.image)
		detector.detect(handle_image, image, object="person")
	else:
		server_thread = threading.Thread(target=start_server)
		server_thread.daemon = True
		server_thread.start()

		detector.stream(handle_stream, object="person", show=False)

if __name__ == "__main__":
	main()