import time
import pycozmo
from PIL import Image
from flask import Flask, Response, render_template, request, jsonify
import json
import threading
import io


app = Flask(__name__)
frame = None
frameout = None

# @app.route('/video')
# def video():
#     return Response(last_im(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


# Last image, received from the robot.
last_im = None

class connection:
    connection_client = pycozmo.Client()
    pycozmo = pycozmo
cli = None


def on_camera_image(cli, new_im):
    """ Handle new images, coming from the robot. """
    global last_im
    last_im = new_im
    last_im

glob_connected = False
reconnect_request = False
# reconnect_event = threading.Event()

# state trackers

# this is for canceling out repeat keypresses
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


# Movement states (separate for each direction)
movement_state = {
    'forward': False,
    'backward': False,
    'left': False,
    'right': False,
    'look_up': False,
    'look_down': False,
    'lift_arm_up': False,
    'lift_arm_down': False
}

modifiers = {
    'fast': False,
    'slow': False,
    'light': False
}



# threads --------------------------------
def webserver():
    app.run(host='0.0.0.0', debug=False)



def cozmoconnect():     
    global glob_connected, cli, reconnect_request
    # int_connected = glob_connected

    # while glob_connected == False:
        
    time.sleep(1)
    print("not connected is looping-------------------------------")
    # def reconnect(reconnect_request):
    # while True:
    # if reconnect_request:
        # del cli
    cli = connection.connection_client
    # if being called from reconnect_request:
    


    try:
        try:
            # cli.start()
            with pycozmo.connect() as cli:

        except Exception as ex:
            print(ex)
        # pycozmo.connect()
        cli.wait_for_robot()
        cli.set_head_angle(angle=0.6)
        time.sleep(1)
        print('head moved')

        # Register to receive new camera images.
        cli.add_handler(pycozmo.event.EvtNewRawCameraImage, on_camera_image)

        # Enable camera.
        cli.enable_camera()
        print('camera enabled')
        glob_connected = True
        reconnect_request = False
        # break
    except Exception as ex:
        print(ex)
            # glob_connected = False
        
            # reconnect(False)
        
        



        



# utils -------------------------------------


# Placeholder functions for robot actions
def move_forward():
    movement_state['forward'] = True
    print("Moving forward")

def stop_forward():
    movement_state['forward'] = False
    print("Stopping forward movement")

def move_left():
    movement_state['left'] = True
    print("Turning left")

def stop_left():
    movement_state['left'] = False
    print("Stopping left turn")

def move_backward():
    movement_state['backward'] = True
    print("Moving backward")

def stop_backward():
    movement_state['backward'] = False
    print("Stopping backward movement")

def move_right():
    movement_state['right'] = True
    print("Turning right")

def stop_right():
    movement_state['right'] = False
    print("Stopping right turn")

def lift_arm_up():
    movement_state['lift_arm_up'] = True
    print("Lifting arm up")
    if modifiers['fast']:
        cli.move_lift(10)
    elif modifiers['slow']:
        cli.move_lift(1)
    else: # normal speed
        cli.move_lift(2)

def lift_arm_down():
    movement_state['lift_arm_down'] = True
    print("Lifting arm down")
    if modifiers['fast']:
        cli.move_lift(-10)
    elif modifiers['slow']:
        cli.move_lift(-1)
    else:
        cli.move_lift(-2)
    

def look_up():
    movement_state['look_up'] = True
    print("Looking up")
    if modifiers['fast']:
        cli.move_head(10)
    elif modifiers['slow']:
        cli.move_head(0.5)
    else:
        cli.move_head(1.5)

def look_down():
    movement_state['look_down'] = True
    print("Looking down")
    if modifiers['fast']:
        cli.move_head(-10)
    elif modifiers['slow']:
        cli.move_head(-0.5)
    else:
        cli.move_head(-1.5)

def stop_arm_movement():
    movement_state['lift_arm_up'] = False
    movement_state['lift_arm_down'] = False
    print("Stopping arm movement")
    cli.move_lift(0)

def stop_looking():
    movement_state['look_up'] = False
    movement_state['look_down'] = False
    print("Stopping looking direction")
    cli.move_head(0)

def move_fast():
    modifiers['fast'] = True
    print("Moving fast")
    

def stop_fast():
    modifiers['fast'] = False
    print("Stopping fast move")

def move_slow():
    modifiers['slow'] = True
    print("Moving slow")

def stop_slow():
    modifiers['slow'] = False
    print("Stopping moving slow")




def reconnect():
    global cli, glob_connected, reconnect_request
    try:
        # cli.del_all_handlers()
        # cli.enable_camera(False)
        print('disconnect')
        # cli.disconnect()
        # cli.conn.send_thread.reset()
        
        reconnect_request = True
        time.sleep(5)

        threading.Thread(target=cozmoconnect).start()

        # cli.stop()
        print('connect')
        # cli.connect()
    except Exception as ex:
        print(ex)
    # time.sleep(5)
    # print('cli deleted')
    # del cli
    # glob_connected = False
    # print('connected set to false')




# Function to handle actions when keys are pressed or released
def handle_key_action(key, action):
    global connected
    # print(key, action)
    match key:
        case 'W':  # Move forward
            if action == 'pressed' and not movement_state['forward']:
                move_forward()
            elif action == 'released':
                stop_forward()
        case 'A':  # Turn left
            if action == 'pressed' and not movement_state['left']:
                move_left()
            elif action == 'released':
                stop_left()
        case 'S':  # Move backward
            if action == 'pressed' and not movement_state['backward']:
                move_backward()
            elif action == 'released':
                stop_backward()
        case 'D':  # Turn right
            if action == 'pressed' and not movement_state['right']:
                move_right()
            elif action == 'released':
                stop_right()
        case 'T':  # Lift arm up
            if action == 'pressed' and not movement_state['lift_arm_up']:
                lift_arm_up()
            elif action == 'released':
                stop_arm_movement()
        case 'G':  # Lift arm down
            if action == 'pressed' and not movement_state['lift_arm_down']:
                lift_arm_down()
            elif action == 'released':
                stop_arm_movement()
        case 'R':  # Look up
            if action == 'pressed' and not movement_state['look_up']:
                look_up()
            elif action == 'released':
                stop_looking()
        case 'F':  # Look down
            if action == 'pressed' and not movement_state['look_down']:
                look_down()
            elif action == 'released':
                stop_looking()
        case 'ENTER': # move fast toggle
            if action == 'pressed' and not modifiers['fast']:
                move_fast()
            elif action == 'released':
                stop_fast()
        case 'SHIFT': #move slow toggle
            if action == 'pressed' and not modifiers['slow']:
                move_slow()
            elif action == 'released':
                stop_slow()
        case 'CUSTOM_RECONNECT':
            print(key, action)
            key_state['CUSTOM_RECONNECT'] = False
            reconnect()
        case _:
            print(f"Unknown key: {key}")





# stream images
def stream_images():
    global reconnect_request
    timer = pycozmo.util.FPSTimer(14)

    print('image loaded')
    while not reconnect_request:
        print('looping', reconnect_request)

        if last_im:
            # Get last image.
            im = last_im
            # print(im)

            im_byte_array = io.BytesIO()
            im.save(im_byte_array, format='JPEG')
            im_byte_array.seek(0)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + im_byte_array.read() + b'\r\n')

        timer.sleep()
        # reconnect_request = False








# flask routes ------------------------------------

# video stream
@app.route('/image')
def stream():
    return Response(stream_images(), mimetype='multipart/x-mixed-replace; boundary=frame')

# index.html
@app.route('/')
def index():
    return render_template('index.html')

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



# RUN THE THREADDSSSSS -------------------------------
if __name__ == "__main__":
     
    #  threading.Thread(target=webserver).start()
    #  threading.Thread(target=webserver).join()
    #  threading.Thread(target=cozmoconnect).start()
    #  threading.Thread(target=cozmoconnect).join()
    #  threading.Thread(target=cozmodriver).start()
    webserver_thread = threading.Thread(target=webserver)
    cozmoconnect_thread = threading.Thread(target=cozmoconnect)

    webserver_thread.start()
    cozmoconnect_thread.start()

    webserver_thread.join()
    cozmoconnect_thread.join()

