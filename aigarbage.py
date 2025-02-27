from flask import Flask, Response
from PIL import Image
import io
import time

app = Flask(__name__)

# Function to generate or fetch the PIL image
def generate_image():
    # Create a simple image with PIL for demonstration purposes
    img = Image.new('RGB', (320, 240), color = (73, 109, 137))
    return img

def stream_images():
    while True:
        # Generate or fetch the current image
        img = generate_image()

        # Convert the image to a byte stream (JPEG format)
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='JPEG')
        img_byte_array.seek(0)

        # Yield the image as a part of the HTTP response (chunked transfer encoding)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_byte_array.read() + b'\r\n')

        # Add a small delay between frames to control the stream rate
        time.sleep(0.1)  # 100ms delay for 10 frames per second

@app.route('/stream')
def stream():
    return Response(stream_images(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    # Basic HTML with an img tag that points to the stream
    return '''
    <html>
        <body>
            <h1>Real-time Image Stream</h1>
            <img src="/stream" width="320" height="240" />
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
