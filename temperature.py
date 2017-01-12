# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 20:42:53 2016

@author: pvkh

Use the webcam and measure the color temperature live
"""

import cv2

# Specify text parameters
fontFace = cv2.FONT_HERSHEY_SIMPLEX # openCV font
fontScale = 2 # scale
org = (60, 60) # position
color = 3 # color

cv2.namedWindow("preview") # open a new openCV window
webcam = cv2.VideoCapture(0) # init VideoCapture object (on/off)

if webcam.isOpened(): # if the camera is already opened by OpenCV, get a frame
    rval, frame = webcam.read()

while rval: # while rval is false 
    cv2.imshow("preview", frame) # display the first 
    rval, frame = webcam.read()
    
    # Averaging RGB values
    B = frame[:,:,0].mean()
    G = frame[:,:,1].mean()
    R = frame[:,:,2].mean()

    # CIE space
    X = (-0.14282)*R + (1.54924)*G + (-0.95641)*B
    Y = (-0.32466)*R + (1.57837)*G + (-0.73191)*B
    Z = (-0.68202)*R + (0.77073)*G + (0.56332)*B

    # Chromaticity
    x = X/(X+Y+Z)
    y = Y/(X+Y+Z)

    n = (x - 0.3320) / (0.1858 - y) # constant for McCamy's formula
    # Correlated color temperature
    CCT = 449*n**3 + 3525*n**2 + 6823.3*n + 5520.33
    
    cv2.putText(frame, str(CCT), org, fontFace, fontScale, color) # Add text

    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break
    
cv2.destroyWindow("preview")