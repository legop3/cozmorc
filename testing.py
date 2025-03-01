import pycozmo
import threading
import time

connected_event = threading.Event()  # Tracks if Cozmo successfully connects
move_event = threading.Event()  # Event to trigger movement based on key state

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

            # Only handle movement when a key event triggers it
            while not disconnect_event.is_set():
                # If there's a change in key state, move accordingly
                if move_event.is_set():
                    movement_handler(cli)
                    move_event.clear()  # Reset event after handling movement
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


def movement_handler(cli):
    # Check key state and handle movement
    fast = False
    slow = False

    if key_state['ENTER']:  # Move fast modifier
        fast = True

    if key_state['SHIFT']:  # Move slow modifier
        slow = True

    if key_state['R']:  # Move lift up
        if fast:
            cli.move_lift(10)
        elif slow:
            cli.move_lift(0.5)
        else:
            cli.move_lift(1.5)

    if key_state['F']:  # Move lift down
        if fast:
            cli.move_lift(-10)
        elif slow:
            cli.move_lift(-0.5)
        else:
            cli.move_lift(-1.5)

    if not key_state['R'] and not key_state['F']:  # Stop lift
        cli.move_lift(0)

    if key_state['T']:  # Move head up
        if fast:
            cli.move_head(10)
        elif slow:
            cli.move_head(0.5)
        else:
            cli.move_head(1.5)

    if key_state['G']:  # Move head down
        if fast:
            cli.move_head(-10)
        elif slow:
            cli.move_head(-0.5)
        else:
            cli.move_head(-1.5)

    if not key_state['T'] and not key_state['G']:  # Stop head
        cli.move_head(0)


def handle_key_action(key, action):
    global disconnect_event, reconnect_event

    if key == 'CUSTOM_RECONNECT' and action == 'pressed':
        print("Reconnection requested.")
        disconnect_event.set()  # Signal disconnection
        reconnect_event.set()  # Signal reconnection
        key_state['CUSTOM_RECONNECT'] = False

    # Trigger movement event if any key state changes
    move_event.set()


# Stream images
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
