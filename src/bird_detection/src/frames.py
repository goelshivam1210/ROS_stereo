#!/usr/bin/env python

'''
rosrun bird_detection frames.py _file:=/home/goelshivam12/Research/Bird_Deterrance/Object_Detection/GOPR0040.avi

'''
import rospy
from sensor_msgs.msg import Image
import cv2
import numpy as np
from cv_bridge import CvBridge, CvBridgeError
import math
from std_msgs.msg import Int32

class Frame:
	def __init__(self, camera=0, n_frames=1):
		self.ctr = 0

		self.bridge = CvBridge()
		if(rospy.has_param("~file")):

			file_name = rospy.get_param("~file")
			rospy.loginfo("file is {}".format(file_name))
			#print 
			self.cap = cv2.VideoCapture(file_name)
		else:
			rospy.loginfo("file not specified, using webcam")
			self.cap = cv2.VideoCapture(camera)
			assert self.cap.isOpened(), "is not connected to camera"
		self.n_frames = n_frames

		self.width = self.cap.get(3)
		self.height = self.cap.get(4)
		# print self.height, "x", self.width

		self.rate = rospy.Rate(20) # Hz frequency update

		self.image_frames_pub = []
		for index in range(n_frames):
			img_pub = rospy.Publisher('/image_raw/frame_{}'.format(index), Image, queue_size=1)
			self.image_frames_pub.append(img_pub)
		self.frame_num_pub = rospy.Publisher('/frame_num',Int32 , queue_size=1)


		rospy.on_shutdown(self.on_shutdown)

	interestFrame = None
	def update(self):
		global prevframe
		#self.n_frames = n_frames

		# fps = self.cap.get(cv2.CAP_PROP_FPS)
		# print "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps)

		ret, frame = self.cap.read()
		

		# if interestFrame is not None:
		# 	frame = interestFrame
		# 	self.ctr = 1367

		# if interestFrame is None and self.ctr == 1367:
		# 	interestFrame = frame

		# print ret
		# print frame.shape
		#gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		if (ret is True):
			cv2.imshow('frame', frame)

			width_slice_size = self.width / (self.n_frames/math.sqrt(self.n_frames))
			height_slice_size = self.height / (self.n_frames/(math.sqrt(self.n_frames)))
			# print height_slice_size, "x", width_slice_size
			start_width = 0
			start_height = 0
			flag = 0
			end_height = 0
			end_width = 0


			cut = int(math.sqrt(self.n_frames))
			# print cut
			for i in range (cut):
				end_height += height_slice_size
				for j in range(cut):
					# print i ,"and", j
					flag += 1
					end_width += width_slice_size
					ros_image = self.bridge.cv2_to_imgmsg(frame[int(start_height):int(end_height), int(start_width):int(end_width)], "rgb8")
			 		self.image_frames_pub[flag-1].publish(ros_image)

			 		# print start_height, end_height, "x",start_width, end_width
			 		start_width = end_width
			 	start_height = end_height
			 	end_width = 0
			 	start_width = 0
			 	#end_height += height_slice_size
			self.frame_num_pub.publish(self.ctr)

			self.ctr += 1
			cv2.waitKey(1)


	def on_shutdown(self):
		cv2.destroyAllWindows()
		self.cap.release()



if __name__ == "__main__":
	rospy.init_node('frames', disable_signals=True)
	frame = Frame()

	while not rospy.is_shutdown():
		frame.update()
		frame.rate.sleep()






