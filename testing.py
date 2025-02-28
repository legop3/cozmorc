import pycozmo
import time

cli = pycozmo.Client()
cli.start()
cli.connect()
cli.wait_for_robot()
# cli.set_head_angle(angle=0.2)
cli.move_head(1)
time.sleep(3)
cli.move_lift(10)
# cli.set_lift_height(height=100)


print(pycozmo.robot.MAX_WHEEL_SPEED.mmps)
print(pycozmo.robot.MAX_HEAD_ANGLE.radians)