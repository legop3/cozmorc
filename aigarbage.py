import pycozmo
import threading
from flask import Flask, Response, render_template, request, jsonify
import io
import time

# Flask app
app = Flask(__name__)

# Global variables (thread-safe)
disconnect_event = threading.Event()
reconnect_event = threading.Event()

# Last camera image
last_im = None

# Key state dictionary
key_state = {
    'W': False,
    'A': False,
    'S': False,
    'D': False,
    'T': False,
    'G': False,
    'R': False,
    'F': False,
    'ENTER': False,
    'SHIFT': False,
    'CUSTOM_RECONNECT': False
}


def on_camera_image(cli, new_im):
    global last_im
    last_im = new_im


def movement_handler(cli):
    if disconnect_event.is_set():
        cli.disconnect()
        return


def handle_key_action(key, action):
    global disconnect_event, reconnect_event

    if key == 'CUSTOM_RECONNECT' and action == 'pressed':
        print("Reconnection requested.")
        disconnect_event.set()  # Signal disconnection
        reconnect_event.set()  # Signal reconnection
        key_state['CUSTOM_RECONNECT'] = False


def cozmo_controller():
    global disconnect_event, reconnect_event

    while True:
        if reconnect_event.is_set():
            reconnect_event.clear()
            disconnect_event.clear()  # Reset disconnect flag

        print("Connecting to Cozmo...")
        try:
            with pycozmo.connect() as cli:
                print("Connected to Cozmo.")
                
                cli.add_handler(pycozmo.event.EvtNewRawCameraImage, on_camera_image)
                cli.enable_camera()
                cli.set_head_angle(pycozmo.MAX_HEAD_ANGLE.radians)
                time.sleep(2)

                while not disconnect_event.is_set():
                    movement_handler(cli)
                    time.sleep(0.1)

                print("Disconnecting from Cozmo...")
                cli.disconnect()
        except Exception as e:
            print(f"Error: {e}")

        print("Waiting for reconnection request...")
        while not reconnect_event.is_set():
            time.sleep(0.5)  # Wait for reconnect trigger


def stream_images():
    while not disconnect_event.is_set():
        timer = pycozmo.util.FPSTimer(14)
        if last_im:
            im_byte_array = io.BytesIO()
            last_im.save(im_byte_array, format='JPEG')
            im_byte_array.seek(0)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + im_byte_array.read() + b'\r\n')
        timer.sleep()
    print("Stopping image stream.")


def webserver():
    app.run(host='0.0.0.0', debug=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/image')
def stream():
    if disconnect_event.is_set():
        return Response('stopped')
    return Response(stream_images(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/key-event', methods=['POST'])
def key_event():
    key = request.json.get('key')
    action = request.json.get('action')  # 'pressed' or 'released'

    if key in key_state:
        if action == 'pressed' and not key_state[key]:
            key_state[key] = True
            handle_key_action(key, action)
        elif action == 'released' and key_state[key]:
            key_state[key] = False
            handle_key_action(key, action)

    return jsonify(key_state)


if __name__ == "__main__":
    cozmo_controller_thread = threading.Thread(target=cozmo_controller, daemon=True)
    webserver_thread = threading.Thread(target=webserver, daemon=True)

    cozmo_controller_thread.start()
    webserver_thread.start()

    cozmo_controller_thread.join()
    webserver_thread.join()
