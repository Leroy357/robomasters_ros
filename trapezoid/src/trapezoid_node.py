#!/usr/bin/env python

# To be run in conjunction with Comm_Kalman.ino
# Arduino file

import serial
import time

# ros imports
import rospy
import tf
from std_msgs.msg import Header
from geometry_msgs.msg import PoseStamped
from trapezoid.srv import *

class Trapezoid:
    def __init__(self, serial_port, baudrate):
        # ---------------- class fields ----------------
        # tx and rx to/from Arduino
        self.tx = [0] * 16
        self.rx = [0] * 16

        # Data to be tx to Arduino
        self.header = 0
        self.feeder_motor_state = 0
        self.friction_motor_state = 0
        self.pitch_req = 0
        self.yaw_req = 0
        self.feeder_motor_pwm = 0
        self.friction_motor_pwm = 0

        # Data to be rx from Arduino
        self.kalAngleX = 0.0
        self.kalAngleY = 0.0
        self.kalAngleZ = 0.0

        # Constant to get more decimal places of float data from Arduino
        # Set equal to floats
        self.kalConstX = 100.0
        self.kalConstY = 100.0
        self.kalConstZ = 100.0

        # ---------------- setup ros ----------------
        # publishers
        self.pub_pose = rospy.Publisher('/trapezoid/pose', PoseStamped, queue_size=10)

        # subscribers
        rospy.Subscriber('/trapezoid/setpoint_pose', PoseStamped, self.handle_turret_pose)

        # services
        rospy.Service('/trapezoid/shoot', Shoot, self.handle_shoot)

        #init the node
        rospy.init_node('trapezoid', anonymous=True)

        # ---------------- setup serial port ----------------
        self.arduinoData = serial.Serial(serial_port, baudrate, timeout=1)

	# reset the arduino on connect
	self.arduinoData.setDTR(True)
	time.sleep(1)
	self.arduinoData.setDTR(False)

        rate = rospy.Rate(10) # 10hz
        while not rospy.is_shutdown():
            # (1) transmit to arduino
            self.arduinoTX()
            
            # (2) receive from arduino (disabled for now)
            #if(self.arduinoData.inWaiting() > 0):
            #    self.arduinoRX()

            # (3) publish kalman pose
            self.publish_pose()
            rate.sleep()


    # Send information to arduino
    def arduinoTX(self):
        print "sending pitch " + str(self.pitch_req)
        self.tx[0] = (self.header >> 8) & 255
        self.tx[1] = self.header & 255
        self.tx[2] = self.feeder_motor_state
        self.tx[3] = self.friction_motor_state
        self.tx[4] = (self.pitch_req >> 8) & 255
        self.tx[5] = self.pitch_req & 255
        self.tx[6] = (self.yaw_req >> 8) & 255
        self.tx[7] = self.yaw_req & 255
        self.tx[8] = (self.feeder_motor_pwm >> 8) & 255
        self.tx[9] = self.feeder_motor_pwm & 255
        self.tx[10] = (self.friction_motor_pwm >> 8) & 255
        self.tx[11] = self.friction_motor_pwm & 255
        self.arduinoData.write(bytearray(self.tx))
        

    # receive information from arduino
    def arduinoRX(self):
        myData = self.arduinoData.read(16)

        # change string representation or rx data to int
        for j in range(len(myData)):
            rx[j] = ord(myData[j])
            
        self.kalAngleX = (( (rx[2] << 8)) | (rx[3] & 255))
        self.kalAngleY = (( (rx[4] << 8)) | (rx[5] & 255))
        self.kalAngleZ = (( (rx[6] << 8)) | (rx[7] & 255))

        # to get correct negative representation of data in Python
        self.kalAngleX = twosComp(16, self.kalAngleX)
        self.kalAngleY = twosComp(16, self.kalAngleY)
        self.kalAngleZ = twosComp(16, self.kalAngleZ)
        
        self.kalAngleX = self.kalAngleX / self.kalConstX
        self.kalAngleY = self.kalAngleY / self.kalConstY
        self.kalAngleZ = self.kalAngleZ / self.kalConstZ


    # -------- subscriber handlers --------
    def handle_turret_pose(self, data):
        # convert received orientation to euler
        quaternion = (
            data.pose.orientation.x,
            data.pose.orientation.y,
            data.pose.orientation.z,
            data.pose.orientation.w)
        euler = tf.transformations.euler_from_quaternion(quaternion)
        roll = euler[0]
        pitch = euler[1]
        yaw = euler[2]

        # convert received radians to int commands
        self.pitch_req = int(pitch * 1000)
        self.yaw_req = int(yaw * 1000)

    # -------- service handlers --------
    def handle_shoot(self, req):
        print "shoot service called"
        print req.pwm_speed
        print req.duration
        # TODO: actually shoot stuff
        return True

    # -------- publishers --------
    def publish_pose(self):
        # !!!!TODO: convert kalman angles to radians (rpy -> xyz)
        roll_send = 0
        pitch_send = 0
        yaw_send = 0

        # convert roll, pitch, yaw to quaternion
        quaternion_send = tf.transformations.quaternion_from_euler(roll_send, pitch_send, yaw_send)

        pose_send = PoseStamped()
        pose_send.header = Header()
        pose_send.pose.orientation.x = quaternion_send[0]
        pose_send.pose.orientation.y = quaternion_send[1]
        pose_send.pose.orientation.z = quaternion_send[2]
        pose_send.pose.orientation.w = quaternion_send[3]

        self.pub_pose.publish(pose_send)

    # -------- "private" functions --------
    # Change negative numbers to
    # correct readable representation in Python
    def twosComp(self, bits, value):
        #if value is negative
        if (value >> 15) == 1:
            value = ~value + 1
            return -(( 1<<bits ) + value)
        else:
            return value

if __name__ == '__main__':
    try:
        Trapezoid('/dev/ttyACM0', 115200)
    except rospy.ROSInterruptException:
        pass