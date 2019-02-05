#####################################################################################
#    _______  _    _   _  __ _   _  _                                               #
#   |__   __|| |  | | | |/ /(_) (_)| |       Technische Hochschule Koeln            #
#      | |   | |__| | | ' /   ___  | | _ __  Cologne University of Applied Science  #
#      | |   |  __  | |  <   / _ \ | || '_ \                                        #
#      | |   | |  | | | . \ | (_) || || | | | Institute of Communication Systems    #
#      |_|   |_|  |_| |_|\_\ \___/ |_||_| |_|                 			    #
#										    #
#         Authors:                                                                  #
#  		Darius Aghili darius.aghili@th-koeln.de				    #
#  		Julian Stüttchen jstuettc@th-koeln.de				    #
#                                                                                   #
#                                                                                   #
#         Copyright (C) 2019                                                	    #
#                                                                                   #
#         Technische Hochschule Koeln - Cologne University of Applied Sciences      #
#         Website: www.th-koeln.de                                   		    #
#                                                                                   #
#####################################################################################

##############################################################################
# Imports
##############################################################################
import cv2
import numpy as np
import os

##############################################################################
# Variables
##############################################################################
#Define input and output video
cap = cv2.VideoCapture('car_movie.mp4')
out = cv2.VideoWriter('analyzed_car_movie.avi',cv2.VideoWriter_fourcc('M','J','P','G') ,60.0,(960,540))

#Define start lane A and B
line_start_A_x = 285
line_start_B_x = 460
laneStartRange = 150
line_start_y = 419

#Define end lane A and B
line_end_A_x = 365
line_end_B_x = 455
laneEndRange = 75
line_end_y = 252

#Threshold of frames for lanes to detect vehicle
th = 6
#threshold of frames between car detection an no detection
clearLaneTH = 4 

#Variables for clear detection of lanes
laneAStartClear = True
laneBStartClear = True
laneAEndClear = True
laneBEndClear = True
laneAStartClearTH = 0
laneBStartClearTH = 0
laneAEndClearTH = 0
laneBEndClearTH = 0

#Arrays for detected vehicles per lane
laneADetection = []
laneBDetection = []

#Vehicle counter
vehiclecounterA = 0
vehiclecounterB = 0

#Measured speed variables
laneASpeed = 0
laneBSpeed = 0

##############################################################################
# Resizing video for better performance
# Reading initial frame to create background Substractor
##############################################################################
ret, frame = cap.read()
frame = cv2.resize(frame, (int(cap.get(3)/2), int(cap.get(4)/2)))
subtractor = cv2.createBackgroundSubtractorMOG2(history=20,varThreshold=25,detectShadows=False)

#Creating dir "vehicles" if not exists
if not os.path.exists("./vehicles"):
	os.makedirs("./vehicles")

##############################################################################
# Resizing video for better performance
# Reading initial frame to create background Substractor
##############################################################################
while(cap.isOpened()):
	#Measument for maximum 5 min (5min * 60s * 60fps)
	if int(cap.get(1)) == 18000:
		break	
	#########################################################
	# Capture frame-by-frame resizing video and substract them by 
	# initial background substractor	
	#########################################################
	ret, frame = cap.read()	
	frame = cv2.resize(frame, (int(cap.get(3)/2), int(cap.get(4)/2)))
	oFrame = frame
	frame = subtractor.apply(frame)

	#########################################################
	# Get average pixel density for each lane
	#########################################################
	laneAStart = 0
	laneBStart = 0
	laneAEnd = 0
	laneBEnd = 0

	for i in range (0,laneStartRange):
		laneAStart = laneAStart + frame[line_start_y,line_start_A_x+i]
		laneBStart = laneBStart + frame[line_start_y,line_start_B_x+i]

	for i in range (0,laneEndRange):
		laneAEnd = laneAEnd + frame[line_end_y,line_end_A_x+i]
		laneBEnd = laneBEnd + frame[line_end_y,line_end_B_x+i]

	laneAStart = int(laneAStart/laneStartRange)
	laneBStart = int(laneBStart/laneStartRange)
	laneAEnd = int(laneAEnd/laneEndRange)
	laneBEnd = int(laneBEnd/laneEndRange)

	#########################################################
	# Detect false inputs
	# Value 75 means speed is less than 80 km/h
	# No speed measurement needed for traffic jam
	#########################################################

	for i in range(0,len(laneADetection)):
		if ((int(cap.get(1))-1)-laneADetection[i]) >= 75:
			print('False detection: Clear lane A')
			laneADetection = []
			laneAStartClear = True
			laneAEndClear = True
			laneAStartClearTH = 0
			laneAEnd = 0
			laneAEndClearTH = 0
			break;

	for i in range(0,len(laneBDetection)):
		if ((int(cap.get(1))-1)-laneBDetection[i]) >= 75:
			print('False detection: Clear lane B')
			laneBDetection = []
			laneBStartClear = True
			laneBEndClear = True
			laneBStartClearTH = 0
			laneBEndClearTH = 0
			laneBEnd = 0
			break;

	#########################################################
	# Detecting clearness of lanes
	# Depends on them, calculating speed
	#########################################################

	############################################
	# Lane A: Start lane clearness detection
	# Begin of lane A speed measurement
	############################################
	if laneAStartClear:
		if laneAStart > th or laneAStart < -th:
			laneAStartClear = False
	else:
		if not (laneAStart > th or laneAStart < -th):
			if laneAStartClearTH == clearLaneTH:
				laneADetection.append(int(cap.get(1))-1)
				laneAStartClear = True
				laneAStartClearTH = 0
			else:
				laneAStartClearTH = laneAStartClearTH +1
		else:
			laneAStartClearTH = 0
	
	############################################
	# Lane A: End lane clearness detection
	# End of lane A speed measurement
	############################################
	if laneAEndClear:
		if laneAEnd > th or laneAEnd < -th:
			if len(laneADetection) > 0:
				if (int(cap.get(1))-1) != laneADetection[0]:
					laneAEndClear = False
	else:
		if not (laneAEnd > th or laneAEnd < -th):
		
			if laneAEndClearTH == clearLaneTH:
				laneAEndClear = True
				laneAEndClearTH = 0
				laneASpeed = round(5184/((int(cap.get(1))-1)-laneADetection[0]),2)
				vehiclecounterA = vehiclecounterA + 1
				print("["+str(int(cap.get(1))-1)+"] Lane A speed: " + str(laneASpeed) + " km/h")
				laneADetection.pop(0)
				pic = oFrame[line_end_y-th-50:line_end_y-th,line_end_A_x:line_end_A_x+laneEndRange]
				cv2.imwrite("./vehicles/"+str(int(cap.get(1))-1)+"_Lane_A_"+str(laneASpeed)+"_kmh.png",pic)
			else:
				laneAEndClearTH = laneAEndClearTH + 1
		else:
			laneAEndClearTH = 0

	############################################
	# Lane B: Start lane clearness detection
	# Begin of lane B speed measurement
	############################################
	if laneBStartClear:
		if laneBStart > th or laneBStart < -th:
			laneBStartClear = False
	else:
		if not (laneBStart > th or laneBStart < -th):
		
			if laneBStartClearTH == clearLaneTH:
				laneBStartClear = True
				laneBStartClearTH = 0
				laneBDetection.append(int(cap.get(1))-1)
			else:
				laneBStartClearTH = laneBStartClearTH +1
		else:
			laneBStartClearTH = 0

	############################################
	# Lane B: End lane clearness detection
	# End of lane B speed measurement
	############################################
	if laneBEndClear:
		if laneBEnd > th or laneBEnd < -th:
			if len(laneBDetection) > 0:
				if (int(cap.get(1))-1) != laneBDetection[0]:
					laneBEndClear = False
	else:
		if not (laneBEnd > th or laneBEnd < -th):
		
			if laneBEndClearTH == clearLaneTH:
				laneBEndClear = True
				laneBEndClearTH = 0
				laneBSpeed = round(5184/((int(cap.get(1))-1)-laneBDetection[0]),2)
				vehiclecounterB = vehiclecounterB + 1
				print("["+str(int(cap.get(1))-1)+"] Lane B speed: " + str(laneBSpeed) + " km/h")
				laneBDetection.pop(0)
				pic = oFrame[line_end_y-th-50:line_end_y-th,line_end_B_x:line_end_B_x+laneEndRange]
				cv2.imwrite("./vehicles/"+str(int(cap.get(1))-1)+"_Lane_B_"+str(laneASpeed)+"_kmh.png",pic)
			else:
				laneBEndClearTH = laneBEndClearTH +1
		else:
			laneBEndClearTH = 0

	#########################################################
	# Drawing lanes and speed stats for user interface
	#########################################################
	#Start lanes
	cv2.line(oFrame, (line_start_A_x, line_start_y), (line_start_A_x+laneStartRange, line_start_y), (0, 0xFF, 0), 2)
	cv2.line(oFrame, (line_start_B_x, line_start_y), (line_start_B_x+laneStartRange, line_start_y), (0, 0xFF, 0), 2)

	#End lanes
	cv2.line(oFrame, (line_end_A_x, line_end_y), (line_end_A_x+laneEndRange, line_end_y), (0, 0xFF, 0), 2)
	cv2.line(oFrame, (line_end_B_x, line_end_y), (line_end_B_x+laneEndRange, line_end_y), (0, 0xFF, 0), 2)

	cv2.putText(oFrame,'Detected vehicles: ' + str(vehiclecounterA),(20, 300),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0, 0, 0xFF),2,cv2.FONT_HERSHEY_SIMPLEX,)
	cv2.putText(oFrame,'Measured speed: ' + str(laneASpeed) + ' km/h',(20, 330),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0, 0, 0xFF),2,cv2.FONT_HERSHEY_SIMPLEX,)

	cv2.putText(oFrame,'Detected vehicles: ' + str(vehiclecounterB),(650, 300),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0xFF, 0, 0xFF),2,cv2.FONT_HERSHEY_SIMPLEX,)
	cv2.putText(oFrame,'Measured speed: ' + str(laneBSpeed) + ' km/h',(650, 330),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0xFF, 0, 0xFF),2,cv2.FONT_HERSHEY_SIMPLEX,)

	#Show and save video (Escape character is 'q')
	cv2.imshow('Videoanalysis',oFrame)
	out.write(oFrame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

print("")
print("Speed measurement is done!")
#When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
