import pycozmo
import threading
from flask import Flask, Response, render_template, request, jsonify
import io
import time


# global variables
disconnect_request = False
last_im = None
app = Flask(__name__)

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
    # print(new_im)
    global last_im
    last_im = new_im
    last_im

    # return

def movement_handler(cli):

    # print('handling movement frame')
    # cli.set_head_angle(angle=0.5)

    return

def handle_key_action(key, action):

    match key:
        case 'CUSTOM_RECONNECT':
            print('reconnect key pressed', key, action)
            disconnect_request = True
            key_state['CUSTOM_RECONNECT'] = False
            print(disconnect_request)
            # reconnect()




def cozmo_controller():
        print("no disconnect request")
        with pycozmo.connect() as cli:
            while not disconnect_request:
                
                # add camera event handler
                cli.add_handler(pycozmo.event.EvtNewRawCameraImage, on_camera_image)
                
                # enable camera
                cli.enable_camera()
                cli.set_head_angle(pycozmo.MAX_HEAD_ANGLE.radians)
                time.sleep(2)
                while not disconnect_request:
                    movement_handler(cli)
                print('movement handler disconnect')
            print('disconnect')

        

def stream_images():
    timer = pycozmo.util.FPSTimer(14)
    while not disconnect_request:

        if last_im:
            # get last image, 1 frame behind
            im = last_im

            im_byte_array = io.BytesIO()
            im.save(im_byte_array, format='JPEG')
            im_byte_array.seek(0)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + im_byte_array.read() + b'\r\n')
        timer.sleep()
    print('disconnecting stream')

def webserver():
    app.run(host='0.0.0.0', debug=False)




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/image')
def stream():
    return Response(stream_images(), mimetype='multipart/x-mixed-replace; boundary=frame')


# keypress handler
@app.route('/key-event', methods=['POST'])
def key_event():
    key = request.json.get('key')
    action = request.json.get('action')  # 'pressed' or 'released'

    if key in key_state:
        # Only change the key state if it's different from the current state
        if action == 'pressed' and not key_state[key]:
            key_state[key] = True
            # Handle the key action
            handle_key_action(key, action)

        elif action == 'released' and key_state[key]:
            key_state[key] = False
            # Handle the key release action
            handle_key_action(key, action)

    # You can also send back the current state of the keys if needed
    return jsonify(key_state)



if __name__ == "__main__":

    cozmo_controller_thread = threading.Thread(target=cozmo_controller)
    webserver_thread = threading.Thread(target=webserver)

    cozmo_controller_thread.start()
    webserver_thread.start()

    cozmo_controller_thread.join()
    webserver_thread.join()