import pycozmo
import time
import threading
from flask import Flask, Response
import io
app = Flask(__name__)



def on_camera_image(cli, new_im):
    """ Handle new images, coming from the robot. """
    global last_im
    last_im = new_im
    last_im

def cozmoconnect():
    cli = pycozmo.Client()
    cli.start()
    cli.connect()
    cli.wait_for_robot()
    cli.enable_camera()
    cli.add_handler(pycozmo.event.EvtNewRawCameraImage, on_camera_image)

def webserver():
    app.run(host='0.0.0.0', debug=False)






# stream images
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

# video stream
@app.route('/image')
def stream():
    return Response(stream_images(), mimetype='multipart/x-mixed-replace; boundary=frame')
# # cli.set_head_angle(angle=0.2)
# cli.move_head(1)
# time.sleep(3)
# cli.move_lift(10)
# # cli.set_lift_height(height=100)


# print(pycozmo.robot.MAX_WHEEL_SPEED.mmps)
# print(pycozmo.robot.MAX_HEAD_ANGLE.radians)

threading.Thread(target=cozmoconnect).start()
threading.Thread(target=webserver).start()
