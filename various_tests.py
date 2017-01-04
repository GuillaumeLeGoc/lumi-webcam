#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 21:06:49 2016

@author: guillaume
"""

import cv2
import numpy as np
import scipy as sp
from matplotlib import pyplot as plt

cam = cv2.VideoCapture(0)

rval, frame = cam.read()
cv2.imshow("Webcam", frame)
plt.imshow(frame)
cv2.destroyWindow("webcam")

#fig1 = plt.figure(1)
#plt.clf()
#plt.imshow(frame)
#cam.release()

#fig1.savefig("camShot.pdf")

#frameR = frame[:,:,0]
#frameG = frame[:,:,1]
#frameB = frame[:,:,2]
#
#fig2 = plt.figure(2)
#plt.subplot(3,1,1)
#plt.imshow(frameR)
#plt.colorbar()
#plt.title("RED")
#plt.subplot(3,1,2)
#plt.imshow(frameG)
#plt.title("GREEN")
#plt.subplot(3,1,3)
#plt.imshow(frameB)
#plt.title("BLUE")
