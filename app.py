import os
import threading
import base64
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from flask import Flask, render_template, request

# Define the directory where images will be uploaded
UPLOAD_DIR = 'static/uploads'
# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Define a custom HTTP request handler for image uploads
class ImageUploadHandler(BaseHTTPRequestHandler):

    # Handle POST requests
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            image_data = self.rfile.read(content_length)
            filename = f'image_{int(time.time())}.jpg'
            
            # Encode image data using base64
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            # Construct the full path to save the image
            full_path = os.path.join(UPLOAD_DIR, filename)
            
            # Write the encoded image data to the file
            with open(full_path, 'wb') as output_file:
                output_file.write(base64.b64decode(encoded_image))
            
            app.logger.info(f"Image '{filename}' saved successfully.")
            
            # Send a response indicating the image has been saved
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body>Image '{filename}' received and saved successfully.</body></html>".encode())
        
        except Exception as e:
            app.logger.error(f"Error while processing image: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body>Error processing image: {str(e)}</body></html>".encode())

# Define the address and port for the HTTP server
server_address = ('0.0.0.0', 5000)

# Function to start the HTTP server
def run_http_server():
    httpd = HTTPServer(server_address, ImageUploadHandler)
    print('HTTP server listening on port 5000...')
    httpd.serve_forever()

# Initialize Flask application
app = Flask(__name__)

# Global variable to store the filename of the last received image
last_received_image = None

# Flask route to display images
@app.route('/')
def display_images():
    global last_received_image
    
    # Update last_received_image with the latest image file
    image_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    if image_files:
        last_received_image = image_files[-1]
    
    print("Last received image file:", last_received_image)
    
    return render_template('display.html', image_file=last_received_image)

# Main execution point
if __name__ == '__main__':
    # Start the HTTP server in a separate thread
    t1 = threading.Thread(target=run_http_server)
    t1.start()

    # Start the Flask app in the main thread
    app.run(debug=True, host='0.0.0.0', port=5001)
