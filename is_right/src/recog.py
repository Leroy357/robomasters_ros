#!/usr/bin/env python
import rospy
import numpy as np
import math
import sys
from sensor_msgs.msg import LaserScan
from aimbot.msg import DetectedRobot
from geometry_msgs.msg import PointStamped
from geometry_msgs.msg import Point

#Finds largest object within a threshold, and publishes the object's
#location as a DetectedRobot message
pub = rospy.Publisher('detect', DetectedRobot, queue_size=100)
wr = rospy.Publisher('newp', PointStamped, queue_size=100)
def move_pos(scan):
    time = 0
    max = 0
    pos = 0
    current_angle = 0
    currentLength = 0
    checkerold = []
    checkernew = [] #temp
    indiceold = []
    indicenew = []#temp
    for i, item in enumerate(scan.ranges):
    	stable = scan.ranges[0]
    	time+=1
    	current_angle = (scan.angle_increment*time)
        if scan.ranges[i] <= (stable)*.5:
            if(currentLength==0):
                checkernew = []
                indicenew = []
            currentLength+=1
            if currentLength > max:
                max = currentLength
            checkernew.append(item)
            indicenew.append(i)
        else:
            if(max==currentLength):
                checkerold = checkernew
                indiceold = indicenew
            currentLength = 0
            stable = scan.ranges[i]
    pos = 0
    shape = len(indiceold)
    if(shape > 0):
	    if(shape %2 ==0):
	    	pos = ((checkerold[shape/2]) + (checkerold[shape/2 - 1]))/2
	    else:
	    	pos = (checkerold[(shape-1)/2])	 
    current_angle = len(indiceold)/2 * scan.angle_increment
   

    pub.publish(distance = pos , y_rotation = current_angle)
    
    
    test_stamped = PointStamped(header = Header(stamp = rospy.Time.now(), frame_id = "move"),
    point = Point(math.cos(current_angle)*pos ,  math.sin(current_angle)*pos, 0))
    wr.publish(test_stamped)
   
    
#just reports how 'wide' the gap between scans gets as distance increases    
def findRatio(angle_increment , length):
	width = ((math.sin(angle_incremenent/2))*length)*2

def listener():
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("/scan", LaserScan, move_pos)
    rospy.spin()


if __name__ == '__main__':
    try:
        listener()
    except rospy.ROSInterruptException:
        pass

   

