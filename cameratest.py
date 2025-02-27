import pycozmo

cli = pycozmo.Client()
cli.start()
cli.connect()
cli.wait_for_robot()
cli.set_head_angle(angle=0.6)

