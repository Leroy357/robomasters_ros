# robomasters_ros

## Get start
1. check if your computer has a catkin workspace in ~/ directory. If not, 

    `mkdir catkin_ws`

    `cd catkin_ws/`

    `mkdir src`

    `cd src/`

    `git clone https://github.com/pico737/robomasters_ros.git`

    `catkin_make` 

2. After you run the `roscore`, open a new terminal and pull the new code from github inside the ~/catkin_ws/src/robomasters_ros

    `catkin_make -DCATKIN_BLACKLIST_PACKAGES="rm_cv;sensor_send"`

    `source devel/setup.bash` (not necessary if it is in ./bashrc)

    `rosrun trapezoid trapezoid_node.py/`
 
3. Test to see if your node is correctly running without error, the serial communication is working, open a new terminal and 

    `rosnode list`

    `rostopic list`
 
    `rosrun trapezoid client.py`
