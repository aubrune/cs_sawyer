#!/usr/bin/env python
# -*- coding: utf-8 -*-


import intera_interface
from std_msgs.msg import UInt8
from std_msgs.msg import Bool
import rospy
import argparse	
import time
import random



class Head_Move(object):


    def __init__(self):

        self._done = False
        self._head = intera_interface.Head()
        # verify robot is enabled
        print("Getting robot state... ")
        self.robot_state = 0 # normal
        self.breath_state =0 # false
        rospy.Subscriber("cs_sawyer/breath", Bool, self.callback_update_breath2)
        rospy.Subscriber("cs_sawyer/head_light", UInt8, self.callback_update_move)
 
    def wobble(self):
        """
        Performs the wobbling
        """
        command_rate = rospy.Rate(1)
        control_rate = rospy.Rate(100)
        while self.robot_state== 0:
            angle = random.uniform(-2.2, -0.3)
            while (not rospy.is_shutdown() and
                   not (abs(self._head.pan() - angle) <=
                       intera_interface.HEAD_PAN_ANGLE_TOLERANCE)):
                self._head.set_pan(angle, speed=0.2, timeout=0)
                if self.robot_state ==0 :
                    break
                control_rate.sleep()
            command_rate.sleep()
        

    def set_neutral(self):
        self._head.set_pan(-0.8, active_cancellation=True)
    

    def set_look_board(self):
        self._head.set_pan(-0.9, active_cancellation=True)


    def callback_update_move(self, msg):
        self.robot_state = msg.data


    def update_move(self):
        if self.robot_state == 0:   # normal
            self.wobble()
        elif self.robot_state == 1 and rospy.get_param("/cs_sawyer/error", "") == "full" :   # error
            self.set_neutral()
        elif self.robot_state == 2 or self.robot_state == 3:  # writing
            self.set_look_board()
    
    def callback_update_breath2(self,msg):
        self.breath_state = msg.data
        if not self.breath_state:
            self.set_neutral() 

            
    def run(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            self.update_move()
            rate.sleep()

if __name__ == '__main__':
    rospy.init_node("cs_sawyer_head_move")
    head_move = Head_Move()
    head_move.run()