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
    # print('handling movement frame')

    # assign fast and slow modifiers
    fast = False
    slow = False

    
    if key_state['ENTER']: #move fast modifier
        fast = True

    if key_state['SHIFT']: #move slow modifier
        slow = True

    if key_state['R']: #move lift up
        if fast:
            cli.move_lift(10)
        elif slow:
            cli.move_lift(0.5)
        else:
            cli.move_lift(1.5)

    if key_state['F']: #move lift down
        if fast:
            cli.move_lift(-10)
        elif slow:
            cli.move_lift(-0.5)
        else:
            cli.move_lift(-1.5)

    if not key_state['R'] and not key_state['F']: #stop lift
        cli.move_lift(0)

    if key_state['T']: #move head up
        if fast:
            cli.move_head(10)
        elif slow:
            cli.move_head(0.5)
        else:
            cli.move_head(1.5)

    if key_state['G']: #move head down
        if fast:
            cli.move_head(-10)
        elif slow:
            cli.move_head(-0.5)
        else:
            cli.move_head(-1.5)

    if not key_state['T'] and not key_state['G']: #stop head
        cli.move_head(0)

    




def handle_key_action(key, action):
    global disconnect_event, reconnect_event

    if key == 'CUSTOM_RECONNECT' and action == 'pressed':
        print("Reconnection requested.")
        disconnect_event.set()  # Signal disconnection
        reconnect_event.set()  # Signal reconnection
        key_state['CUSTOM_RECONNECT'] = False


# def cozmo_controller():
#     global disconnect_event, reconnect_event

#     while True:
#         if reconnect_event.is_set():
#             reconnect_event.clear()
#             disconnect_event.clear()  # Reset disconnect flag

#         print("Connecting to Cozmo...")
#         try:
#             with pycozmo.connect() as cli:
#                 print("Connected to Cozmo.")
                
#                 cli.add_handler(pycozmo.event.EvtNewRawCameraImage, on_camera_image)
#                 cli.enable_camera()
#                 cli.set_head_angle(pycozmo.MAX_HEAD_ANGLE.radians)
#                 time.sleep(2)

#                 while not disconnect_event.is_set():
#                     movement_handler(cli)
#                     time.sleep(0.05)

#                 print("Disconnecting from Cozmo...")
#                 cli.disconnect()
#         except Exception as e:
#             print(f"Error: {e}")

#         print("Waiting for reconnection request...")
#         while not reconnect_event.is_set():
#             time.sleep(0.5)  # Wait for reconnect trigger



# # Global threading events for managing connection states
# disconnect_event = threading.Event()
# reconnect_event = threading.Event()

# def cozmo_controller():
#     global disconnect_event, reconnect_event

#     retry_delay = 1  # Initial delay before retrying (in seconds)
#     max_delay = 30   # Maximum delay before retrying

#     while True:
#         if reconnect_event.is_set():
#             reconnect_event.clear()
#             disconnect_event.clear()  # Reset disconnect flag

#         print("Attempting to connect to Cozmo...")

#         try:
#             with pycozmo.connect() as cli:
#                 print("Connected to Cozmo.")

#                 cli.add_handler(pycozmo.event.EvtNewRawCameraImage, on_camera_image)
#                 cli.enable_camera()
#                 cli.set_head_angle(pycozmo.MAX_HEAD_ANGLE.radians)
#                 time.sleep(2)

#                 retry_delay = 1  # Reset retry delay after successful connection

#                 while not disconnect_event.is_set():
#                     movement_handler(cli)
#                     time.sleep(0.1)

#                 print("Disconnecting from Cozmo...")
#                 cli.disconnect()

#         except Exception as e:
#             print(f"Connection failed: {e}")
#             print(f"Retrying in {retry_delay} seconds...")
#             time.sleep(retry_delay)
#             retry_delay = min(retry_delay * 2, max_delay)  # Exponential backoff

#         print("Waiting for reconnection request...")
#         while not reconnect_event.is_set():
#             time.sleep(0.5)  # Wait for reconnect trigger

# +_+_+_+_+_+_+_+_+_+_+_+_+_


import pycozmo
import threading
import time

connected_event = threading.Event()  # Tracks if Cozmo successfully connects

def cozmo_thread():
    """Function to run Cozmo connection inside a separate thread."""
    global connected_event
    try:
        with pycozmo.connect() as cli:
            print("Connected to Cozmo.")
            connected_event.set()  # Mark successful connection

            cli.add_handler(pycozmo.event.EvtNewRawCameraImage, on_camera_image)
            cli.enable_camera()
            cli.set_head_angle(pycozmo.MAX_HEAD_ANGLE.radians)
            time.sleep(2)

            while not disconnect_event.is_set():
                movement_handler(cli)
                time.sleep(0.1)

            print("Disconnecting from Cozmo...")
            cli.disconnect()
            connected_event.clear()  # Reset when disconnected

    except Exception as e:
        print(f"Cozmo thread encountered an error: {e}")
        connected_event.clear()  # Ensure we retry on failure

def cozmo_controller():
    retry_delay = 1  # Initial delay before retrying
    max_delay = 30   # Maximum retry delay

    while True:
        print("Starting Cozmo connection thread...")
        thread = threading.Thread(target=cozmo_thread, daemon=True)
        thread.start()

        thread.join(timeout=15)  # Wait for connection (max 15 sec)

        if not connected_event.is_set():  # Only restart if it never connected
            print("Cozmo connection failed or is stuck. Restarting thread...")
            disconnect_event.set()  # Signal disconnect
            thread.join()  # Ensure the thread stops before restarting
            disconnect_event.clear()  # Reset for the next attempt

            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_delay)  # Exponential backoff
        else:
            print("Cozmo is connected and running. No need to restart.")
            thread.join()  # Keep thread running normally


# +_+_+_+_+_+_+_+_+_+_+_+_+_
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
