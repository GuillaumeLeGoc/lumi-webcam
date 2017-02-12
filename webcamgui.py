#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:40:56 2017

Attempt to get two classes, one for the GUI and one for the driver.

@author: pvkh
"""

# import libraries
from __future__ import division
import pyqtgraph as pg
import sys
import cv2
import numpy as np
from PyQt4 import QtGui

#%%############################################################################
###############################################################################

class WebcamDriver():
    """ This class contains functions which drive the webcam through OpenCV.
    It allows the user to take snapshots with the webcam and analyze the
    the picture: color temperature, RGB content.
    """
    
    def __init__(self):
        """
        """
        
        # Constants definition
        self.x_e = 0.3366
        self.y_e = 0.1735
        self.A_0 = -949.86315
        self.A_1 = 6253.80338
        self.t_1 = 0.92159
        self.A_2 = 28.70599
        self.t_2 = 0.20039
        self.A_3 = 0.00004
        self.t_3 = 0.07125
        
    def openWebcam(self):
        """ This function connects the webcam with OpenCV.
        """
        
        # Connect the webcam with OpenCV
        self.webcam = cv2.VideoCapture(self.device_id)
        
    def takeFrame(self):
        """ This function takes a snapshot with the webcam and convert it to
        RGB.
        """
        
        # Take a snapshot with the webcam
        self.isRead, self.frame = self.webcam.read()
        
        # OpenCV conversion to RGB from BGR
        self.frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        
    def rgbLevels(self):
        """ This functions converts a BGR picture to RGB picture, splits the
        three channels into single ones and calculate RGB levels and means.
        """
        
        # Split RGB channels
        self.R, self.G, self.B = cv2.split(self.frame_rgb)
        
        # Compute RGB means
        self.R_mean = int(round( self.R.mean() ))
        self.G_mean = int(round( self.G.mean() ))
        self.B_mean = int(round( self.B.mean() ))
        
    def cieXYZ(self):
        """ This function converts the picture from RGB color space to 
        CIE XYZ tristimulus color space through the transformation matrix.
        """
        
        # Denominator of the transformation matrix
        den = (1/0.17697)
        
        # Transformation matrix
        self.X = den*((0.49)*self.R + (0.31)*self.G + (0.2)*self.B)
        self.Y = den*((0.17697)*self.R + (0.8124)*self.G + (0.01063)*self.B)
        self.Z = den*((0)*self.R + (0.010)*self.G + (0.99)*self.B)
        
        # Y corresponds to the illuminance
        self.illuminance_mean = int(round( self.Y.mean() ))
        
    def ciexy(self):
        """ This function converts the picture from CIE XYZ color space to the
        chromaticities xy.
        """
        
        self.x = self.X/(self.X + self.Y + self.Z)
        self.y = self.Y/(self.X + self.Y + self.Z)
        
    def cctAnalysis(self):
        """ This function calculates the correlated color temperature (CCT) of
        each pixel of the frame. It is estimated with the Hernandez-Andrés (HA)
        formula.
        """
        
        # McCamy's parameter to evaluate CCT
        self.n_HA = (self.x - self.x_e)/(self.y - self.y_e)
        
        # HA formula
        self.cct = ( self.A_0 + self.A_1*np.exp(-self.n_HA/self.t_1) + 
                                self.A_2*np.exp(-self.n_HA/self.t_2) + 
                                self.A_3*np.exp(-self.n_HA/self.t_3) )
        
        # Delete too high values
        self.cct[self.cct > 30000] = 0
        
        # Compute CCT mean
        self.cct_mean = int(round( self.cct.mean() ))
    
    def rgbHistogram(self):
        """ This function calculates the histogram for RGB pixels values
        distribution.
        """
        
        # Define color map
        colors = [ (255,0,0),(0,255,0),(0,0,255) ]
        # Define empty image to plot histogram in
        plot_to_fill = np.zeros((280,400,3))
        # Define bins of the histogram
        bins = np.arange(256).reshape(256,1)
        
        # Loop on RGB channels
        for channel, color in enumerate(colors):
            # Make the histogram
            hist_item = cv2.calcHist(self.frame,[channel],None,[256],[0,256])
            
            # Normalisation
            cv2.normalize(hist_item,hist_item,0,255,cv2.NORM_MINMAX)
            
            # Draw the histogram as a picture
            hist = np.int32(np.around(hist_item))
            pts = np.int32(np.column_stack((bins, hist)))
            cv2.polylines(plot_to_fill, [pts], False, color)
        
        # Flip and convert tot iunt8
        self.rgb_histo = np.flipud(plot_to_fill)
        self.rgb_histo = np.uint8(self.rgb_histo)
        
#%%############################################################################
###############################################################################

class WebcamGui(QtGui.QWidget):
    """ This class uses WebcamDriver class and embed its function in Qt graphic
    user interface (GUI).
    """
    
    def __init__(self):
        """
        """
        
        super(WebcamGui, self).__init__()
        
        # Call WebcamDriver
        self.driver = WebcamDriver()
        
        # Call the gui initialization
        self.initWindow()
        
    def initWindow(self):
        """ Creates the main window, adds widgets and connect them to methods.
        """

        # Initialize a grid layout
        grid_layout = QtGui.QGridLayout()
        # Defince space between widgets
        grid_layout.setSpacing(10)
        
        # Create buttons
        button_connect = QtGui.QPushButton('Connect/Disconnect webcam', self)
        button_save = QtGui.QPushButton('Save as picture', self)
        button_start = QtGui.QPushButton('Start stream',self)
        button_stop = QtGui.QPushButton('Stop stream',self)
        
        # Device ID
        self.device_id_label = QtGui.QLabel('Enter webcam device ID')
        self.device_id_text = QtGui.QLineEdit('0', self)
        
        # Webcam canvas
        self.snap_canvas = pg.ImageView()
        
        # Histogram canvas (RGB)
        #self.hist_canvas = pg.ImageView()
        
        # Temperature canvas
        self.temp_canvas = pg.ImageView()
        
        # Text boxes
        self.cct_label = QtGui.QLabel(self)
        self.red_label = QtGui.QLabel(self) # hips
        self.green_label = QtGui.QLabel(self)
        self.blue_label = QtGui.QLabel(self)
        self.illuminance_label = QtGui.QLabel(self)
        self.messages_to_user = QtGui.QLabel(self)
        self.cct_roi_label = QtGui.QLabel(self)
        self.x_label = QtGui.QLabel(self)
        self.y_label = QtGui.QLabel(self)
                
        # Add buttons to the layout
        grid_layout.addWidget(button_connect, 0, 0, 1, 1)
        grid_layout.addWidget(button_start, 0, 1, 1, 1)
        grid_layout.addWidget(button_stop, 0, 2, 1, 1)
        grid_layout.addWidget(button_save, 0, 3, 1, 1)
        
        # Text input pour ID de la caméra
        grid_layout.addWidget(self.device_id_label, 0, 4, 1, 1)
        grid_layout.addWidget(self.device_id_text, 0, 5, 1, 1)
        
        # Canvas pour l'image de la caméra et températures
        grid_layout.addWidget(self.snap_canvas, 1, 0, 1, 2)
        grid_layout.addWidget(self.temp_canvas, 1, 2, 1, 5)
        
        # Moyennes RGB et illuminance
        grid_layout.addWidget(self.cct_label, 14, 2, 1, 1)
        grid_layout.addWidget(self.cct_roi_label, 15, 2, 1, 1)
        grid_layout.addWidget(self.red_label, 15, 0, 1, 1)
        grid_layout.addWidget(self.green_label, 16, 0, 1, 1)
        grid_layout.addWidget(self.blue_label, 17, 0, 1, 1)
        grid_layout.addWidget(self.illuminance_label, 18, 0, 1, 1)
        grid_layout.addWidget(self.x_label,16,2,1,1)
        grid_layout.addWidget(self.y_label,17,2,1,1)
        
        # Verbose
        grid_layout.addWidget(self.messages_to_user, 20,1,1,10)
        
        # Ajout du layout sur la fenêtre principale
        self.setLayout(grid_layout)
        
        # Shape of the window        
        self.setGeometry(300, 300, 1000, 800) # x, y, W, H
        self.setWindowTitle("Webcam Analyzer") # Titre de la fenêtre  
        self.setWindowIcon(QtGui.QIcon("webcam-512.png")) # Icone
        
        # Connect buttons to functions        
        button_connect.clicked.connect(self.openWebcam)
        button_start.clicked.connect(self.startStream)
        button_stop.clicked.connect(self.stopStream)
        button_save.clicked.connect(self.savePicture)
        
        # Display the gui on the screen
        self.show()
        
    def printToUser(self, message):
        """ This function displays information to the user directly within the
        GUI window.
        """
        
        self.messages_to_user.setText(message)
        self.messages_to_user.adjustSize()
        
        
    def openWebcam(self):
        """ This function calls WebcamDriver openWebcam method and passes it
        the webcam device ID.
        """
        
        # Get the webcam device ID from the input text box
        self.driver.device_id = int(self.device_id_text.text())
        
        # Call WebcamDriver openWebcam method
        self.driver.openWebcam()
        
        # Verbose
        self.printToUser("Webcam #"+str(self.driver.device_id)+" connected.")
        
    def startStream(self):
        """ This function streams frames from the webcam to the GUI window by
        calling WebcamDriver takeFrame method in a loop.
        """
        
        try:
            # Check if the webcam is connected
            if self.driver.webcam.isOpened():
                
                # Get the first frame
                self.driver.takeFrame()
                
                # Initialize the play/stop indicator
                self.webcam_break_loop = False
                
                # Initialize the calculation indicator
                self.indice = 0 
                
                # Verbose
                self.printToUser("Starting stream.")
                
                # Active loop if webcam still active
                while self.driver.isRead: 
                    
                    # Record a frame from the webcam               
                    self.driver.takeFrame()
                    
                    # Display webcam frame
                    self.snap_canvas.setImage(self.driver.frame_rgb.transpose(
                                                                [1,0,2]),
                                                
                                              )
                    # Hide histogram
                    self.snap_canvas.ui.histogram.hide()
                    self.snap_canvas.ui.menuBtn.hide()
                    self.snap_canvas.ui.roiBtn.hide()
                    

                    # Make the RGB levels analysis anc CCT calculation once in
                    # 2 pictures
                    if self.indice == 2:
                        
                        # RGB levels analysis
                        self.driver.rgbLevels()
                        
                        # Display RGB means
                        self.red_label.setText("Mean RED: "+str(
                                                        self.driver.R_mean))
                        self.red_label.adjustSize()
                        self.green_label.setText("Mean GREEN: "+str(
                                                        self.driver.G_mean))
                        self.green_label.adjustSize()
                        self.blue_label.setText("Mean BLUE: "+str(
                                                        self.driver.B_mean))
                        self.blue_label.adjustSize()
                        
                        # Calculate the rgb levels distribution histogram
                        #self.driver.rgbHistogram()
                        
                        # Calculate picture in CIE XYZ color space
                        self.driver.cieXYZ()
                        
                        # Caclulate picture in CIE xy chomaticities
                        self.driver.ciexy()
                    
                        # Calculate CCT
                        self.driver.cctAnalysis()
                        
                        # Display CCT mean value and mean illuminance
                        self.cct_label.setText("Mean color temperature: "+
                                               str(self.driver.cct_mean))
                        self.cct_label.adjustSize()
                        self.illuminance_label.setText("Mean illuminance: "+
                                                str(
                                                self.driver.illuminance_mean))
                        self.illuminance_label.adjustSize()
                        
                        # Display CCT map
                        self.temp_canvas.setImage(self.driver.cct.transpose(),
                                                  levels=(0,15000))
                        self.temp_canvas.ui.menuBtn.hide()
                        self.temp_canvas.ui.histogram.setHistogramRange(
                                                                    0, 15000)
                        
                        # Calculate the mean in Region of Interest
                        self.getMeanInRoi()
                        
                        if self.cct_roi_curve != (None, None):
                            self.cct_roi_label.setText("Mean color Temperature"
                                                       + " in ROI: "
                                                       + str(
                                                           self.cct_roi_average
                                                           ))
                            self.cct_roi_label.adjustSize()
                          
                        # Calculate the mean (on all picture) x and y
                        self.x_label.setText("x: " + str(self.driver.x.mean()))
                        self.x_label.adjustSize()
                        self.y_label.setText("y: " + str(self.driver.y.mean()))
                        
                        # Réinitialiser l'indice
                        self.indice = 0
                        
                    else:
                        # Don't make any calculation
                        pass

                    # Increment calculation indicator
                    self.indice += 1
                    
                    # Wait 20 ms
                    cv2.waitKey(20)
                    
                    if self.webcam_break_loop:
                        self.printToUser("Streaming stopped.")
                        break
            else:
                self.printToUser("Connect webcam first...")
        except AttributeError:
            self.printToUser("Connect webcam first.")
            
    def stopStream(self):
        """ This function pauses the webcam stream.
        """
        
        try:
            if not self.webcam_break_loop:
                self.webcam_break_loop = True
                self.printToUser("Stopping stream...")
            else:
                self.printToUser("Stream not running...")
        except AttributeError:
            self.printToUser("Stream not running.")
            
    def savePicture(self):
        """ This function opens a dialog box to save the current webcam frame.
        One has to specify the extension.
        """
        
        self.file_name = QtGui.QFileDialog.getSaveFileName(self, 
                                        "Save as... (specify extension)", "")
        cv2.imwrite(self.file_name, self.driver.frame)
        
    def getMeanInRoi(self):
        """ Calculate the mean color temperature in the region of interested
        selected by the user.
        """
        
        self.cct_roi_curve = self.temp_canvas.roiCurve.getData()
        if self.cct_roi_curve != (None, None):
            self.cct_roi_average = self.cct_roi_curve[1].mean()
        
#%%############################################################################
###############################################################################
        
#def main():
#    qtapp = QtGui.QApplication(sys.argv)
#    gui = WebcamGui()
#    sys.exit(qtapp.exec_())
#    
#if __name__ == '__main__':
#    main()

gui = WebcamGui()