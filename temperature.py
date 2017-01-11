#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 21:11:33 2017

@author: guillaume
"""
# Tentative de mesure de la température d'une image prise avec la webcam
# Utilisation des formules CIE 1931, coefficients de TAOS
# The code can be executed once, then spyder needs to be restart for unknown reason
# WARNING : Images enregistrées par OpenCV au format (BGR), ie:
    # image[:,:,0] = BLUE
    # image[:,:,1] = GREEN
    # image[:,:,2] = RED

import cv2

try:
    webcam
except NameError:
    webcam = cv2.VideoCapture(0)

retval, image = webcam.read() # prendre une frame avec la camera

cv2.imshow("snapshot",image)

print("Max B ="+str(image[:,:,0].max()))
print("Max G ="+str(image[:,:,1].max()))
print("Max R ="+str(image[:,:,2].max()))

# Averaging RGB values
B = image[:,:,0].mean()
G = image[:,:,1].mean()
R = image[:,:,2].mean()

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
print "Supposed temperature in kelvin="+str(CCT)
