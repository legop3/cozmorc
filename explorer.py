import time
import pycozmo
from PIL import Image
from flask import Flask, Response, render_template
import cv2
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


cli = pycozmo.Client()

def on_camera_image(cli, new_im):
    """ Handle new images, coming from the robot. """
    global last_im
    last_im = new_im
    last_im



# threads --------------------------------
def webserver():
    app.run(host='0.0.0.0', debug=False)



def cozmoconnect():
        cli.start()
        cli.connect()
        cli.wait_for_robot()

        cli.set_head_angle(angle=0.6)
        time.sleep(1)
        print('head moved')

        # Register to receive new camera images.
        cli.add_handler(pycozmo.event.EvtNewRawCameraImage, on_camera_image)

        # Enable camera.
        cli.enable_camera()
        print('camera enabled')


# utils -------------------------------------
def stream_images():

    timer = pycozmo.util.FPSTimer(14)

    print('image loaded')
    while True:
        # print('looping')

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






# flask routes ------------------------------------
@app.route('/image')
def stream():
    return Response(stream_images(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')


# RUN THE THREADDSSSSS -------------------------------
if __name__ == "__main__":
     
     threading.Thread(target=webserver).start()
     threading.Thread(target=cozmoconnect).start()
    #  threading.Thread(target=videostream).start()
