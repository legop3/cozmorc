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


def webserver():
    app.run(host='0.0.0.0', debug=False)

@app.route('/image')
def stream():
    return Response(stream_images(), mimetype='multipart/x-mixed-replace; boundary=frame')




@app.route('/')
def index():
    # Basic HTML with an image element, which will be continuously updated by the /image endpoint
    return '''
    <html>
        <body>
            <h1>Live Image Stream</h1>
            <img src="/image" width="320" height="240" />
        </body>
    </html>
    '''

def cozmoconnect():
        cli.start()
        cli.connect()
        cli.wait_for_robot()
        

        # def gen():

        cli.set_head_angle(angle=0.6)
        time.sleep(1)
        print('head moved')

        # Register to receive new camera images.
        cli.add_handler(pycozmo.event.EvtNewRawCameraImage, on_camera_image)

        # Enable camera.
        cli.enable_camera()
        print('camera enabled')


        # Run with 14 FPS. This is the frame rate of the robot camera.
        # @app.route('/video')
            # return Response('test')

        
def stream_images():

    timer = pycozmo.util.FPSTimer(14)

    print('image loaded')
    while True:
        # print('looping')

        if last_im:
            # Get last image.
            im = last_im
            # print(im)
            # im = im.convert('1')
            im_byte_array = io.BytesIO()
            im.save(im_byte_array, format='JPEG')
            im_byte_array.seek(0)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + im_byte_array.read() + b'\r\n')

            # return Response(im_byte_array, mimetype='image/jpeg')
            
            # ret, jpeg = cv2.imencode('.jpg', im)
            # frameout = jpeg.tobytes
            # frameout = pycozmo.camera.minigray_to_jpeg(im, 320, 240)
            # frameout = "test"
            # return (b'--frame\r\n'
            #         b'Content-Type: image/jpeg\r\n\r\n' + frameout + b'\r\n\r\n')
            # yield "test"

            # video(im)
            # Resize from 320x240 to 68x17. Larger image sometime are too big for the robot receive buffer.
            # im = im.resize((68, 17))
            # # Convert to binary image.
            # im = im.convert('1')
            # # Mirror the image.
            # im = im.transpose(Image.FLIP_LEFT_RIGHT)
            # # Construct a 128x32 image that the robot can display.
            # im2 = Image.new("1", (128, 32))
            # im2.paste(im, (30, 7))
            # # Display the result image.
            # cli.display_image(im2)
            # return Response('test')
        timer.sleep()

    # app.route('/video')(videofeed)


# def videostream():
#     @app.route('/video')
#     def streamer():
#         return Response(videocapture(),mimetype='multipart/x-mixed-replace; boundary=frame')
#     # @app.route('/video')
#     # def stream():
#     #     return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')







# RUN THE THREADDSSSSS
if __name__ == "__main__":
     
     threading.Thread(target=webserver).start()
     threading.Thread(target=cozmoconnect).start()
    #  threading.Thread(target=videostream).start()
