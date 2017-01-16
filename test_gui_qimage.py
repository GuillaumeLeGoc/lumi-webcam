#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 10:30:06 2017

Creating GUI

@author: pvkh
"""

from __future__ import division

import sys
import cv2
import numpy as np
from PyQt4 import QtGui


class WebcamGui(QtGui.QWidget): # création de la classe héritant de QWidget
    """ Cette classe gère l'interface graphique principale qui affiche l'entrée
    d'une webcam et analyse les composantes RGB ainsi que la luminosité et la
    température. Elle contient des fonctions utilisant la bibliothèque OpenCV.
    """
    
    def __init__(self):
        
        # __init__ du parent
        super(WebcamGui, self).__init__()
        
        self.initWindow()
        
    def initWindow(self):
        """ Creates the main window, adds widgets and connect them to methods
        """
        
        ##############################
        ### Création de la fenêtre ###
        ##############################
        
        # Layout en grille
        grid_layout = QtGui.QGridLayout()
        # Espace entre les widgets
        grid_layout.setSpacing(8)
        
        ############################
        ### Création des widgets ###
        ############################
        
        # Boutons
        button_connect = QtGui.QPushButton('Connect webcam', self)
        button_save = QtGui.QPushButton('Save as picture', self)
        button_start = QtGui.QPushButton('Start stream',self)
        button_stop = QtGui.QPushButton('Stop stream',self)
        
        # Device ID
        self.device_id_text = QtGui.QLabel('Enter webcam device ID')
        self.device_id_box = QtGui.QLineEdit('0', self)
        self.device_id = int(self.device_id_box.text())
        
        # webcam canvas
        self.img_label = QtGui.QLabel(self)
        
        # histogram canvas
        self.his_label = QtGui.QLabel(self)
        
        # Text boxes
        self.temp_label = QtGui.QLabel(self)
        self.red_label = QtGui.QLabel(self) # hips
        self.green_label = QtGui.QLabel(self)
        self.blue_label = QtGui.QLabel(self)
        self.illuminance_label = QtGui.QLabel(self)
        self.messages_to_user = QtGui.QLabel(self)
        
        #########################
        ### Ajout des widgets ###
        #########################
        
        grid_layout.addWidget(button_connect, 0, 0, 1, 1)
        grid_layout.addWidget(button_start, 0, 1, 1, 1)
        grid_layout.addWidget(button_stop, 0, 2, 1, 1)
        grid_layout.addWidget(button_save, 0, 3, 1, 1)
        grid_layout.addWidget(self.img_label, 1, 0, 9, 9)
        grid_layout.addWidget(self.his_label, 2, 10, 5, 5)
        grid_layout.addWidget(self.temp_label, 7, 10, 1, 1)
        grid_layout.addWidget(self.red_label, 8, 10, 1, 1)
        grid_layout.addWidget(self.green_label, 9, 10, 1, 1)
        grid_layout.addWidget(self.blue_label, 10, 10, 1, 1)
        grid_layout.addWidget(self.messages_to_user, 15,1,1,10)
        grid_layout.addWidget(self.device_id_text, 0, 5, 1, 1)
        grid_layout.addWidget(self.device_id_box, 0, 6, 1, 1)
        grid_layout.addWidget(self.illuminance_label,11, 10, 1, 1)
        
        
        # Ajout du layout sur la fenêtre principale
        self.setLayout(grid_layout)
        
        #################################
        ### Paramètres de l'interface ###
        #################################
        
        self.setGeometry(300, 300, 800, 600) # x, y, W, H; move+resize method
        self.setWindowTitle("Webcam Analyzer") # Titre de la fenêtre  
        self.setWindowIcon(QtGui.QIcon("webcam-512.png")) # Icone
        
        ########################################
        ### Fonctions connectées aux boutons ###
        ########################################
        
        button_connect.clicked.connect(self.openWebcam)
        button_start.clicked.connect(self.startStream)
        button_stop.clicked.connect(self.stopStream)
        button_save.clicked.connect(self.savePicture)
        
        #################################
        ### Définitions de constantes ###
        #################################
        
        self.x_e = 0.3366
        self.y_e = 0.1735
        self.A_0 = -949.86315
        self.A_1 = 6253.80338
        self.t_1 = 0.92159
        self.A_2 = 28.70599
        self.t_2 = 0.20039
        self.A_3 = 0.00004
        self.t_3 = 0.07125
        
        #################################
        ### Afficher le GUI à l'écran ###
        #################################
        
        self.show()
        
        
    #######################################################
    ############### DEFINITION DES METHODES ###############
    #######################################################
    
    def openWebcam(self):
        """ Open webcam through OpenCV.
        """
        
        try: # Vérifier si l'attribut webcam existe
            if self.webcam.isOpened():
                self.printToUser("Webcam already connected.")
            else:
                self.webcam = cv2.VideoCapture(self.device_id) # Créer un objet OpenCV
                self.printToUser("Webcam connected.")
        except AttributeError:
            self.webcam = cv2.VideoCapture(self.device_id)
            self.printToUser("Webcam connected.")
            
    def startStream(self):
        """ Begin webcam stream.
        """
        
        try: # Vérifier si l'attribut existe, autrement prévenir l'utilisateur.
            if self.webcam.isOpened(): # vérifie si la camera est bien connectée
                self.isRead, self.webcam_frame = self.webcam.read() # tenter une 
                # première capture
                self.webcam_break_loop = False # initialiser le témoin de on/off
                self.printToUser("Starting stream.")
                while self.isRead: # boucle pour streamer la webcam
                    
                    # Récupère une frame de la webcam                
                    self.isRead, self.frame = self.webcam.read()
                    
                    # Conversion BGR > RGB
                    self.frame_rgb = cv2.cvtColor(self.frame, 
                                                         cv2.COLOR_BGR2RGB)
                    
                    # Calcul de la moyenne des niveaux de R,G,B
                    self.averageRGB()
                    
                    # Affichage des moyennes R, G, B
                    self.showAverageRGB()
                    
                    # Calcul et affichage de la température de couleurs
                    self.calculateTemperature()
                    
                    # Calcul de l'histogramme
                    self.calculateHistogram()
                    
                    # Conversion de l'image OpenCV en image QImage
                    self.frame_qpix = self.convertToQPixelmap(self.frame_rgb)
                    
                    # Affichage de l'image sur le canvas du GUI
                    self.img_label.setPixmap(self.frame_qpix)
                    
                    # Affichage de l'histogramme
                    self.his_label.setPixmap(self.histplot_qpix)
                                                                    
                    cv2.waitKey(20) # laisser le temps d'appuyer sur "stop"
                    if self.webcam_break_loop:
                        self.printToUser("Streaming stopped.")
                        break
            else:
                self.printToUser("Connect webcam first...")
        except AttributeError:
            self.printToUser("Connect webcam first.")

    def stopStream(self):
        """ Stop webcam stream.
        """
        
        try:
            if not self.webcam_break_loop:
                self.webcam_break_loop = True
                self.printToUser("Stopping stream...")
            else:
                self.printToUser("Stream not running...")
        except AttributeError:
            self.printToUser("Stream not running.")
            
    def averageRGB(self):
        """Get the mean Red, Green and Blue in webcame frame.
        """
        
        # Calcul des moyennes
        self.R, self.G, self.B = cv2.split(self.frame_rgb)
        self.R = self.R.mean()
        self.G = self.G.mean()
        self.B = self.B.mean()
    
    def showAverageRGB(self):
        """ Shows mean values of RGB channels next to the frame from the webcam.
        """
        
        # Affichage dans les boxes
        self.red_label.setText("Mean RED: "+str(int(round(self.R.mean()))))
        self.red_label.adjustSize()
        self.green_label.setText("Mean GREEN: "+str(int(round(self.G.mean()))))
        self.green_label.adjustSize()
        self.blue_label.setText("Mean BLUE: "+str(int(round(self.B.mean()))))
        self.blue_label.adjustSize()
            
    def calculateTemperature(self):
        """ Calculate mean color temperature.
        """
        
        # CIE XYZ space
        self.X = (1/0.17697)*((0.49)*self.R + (0.31)*self.G + (0.2)*self.B)
        self.Y = (1/0.17697)*((0.17697)*self.R + (0.81240)*self.G + (0.01063)*self.B)
        self.Z = (1/0.17697)*((0)*self.R + (0.010)*self.G + (0.99)*self.B)

        # CIE Chromaticities xy
        self.x = self.X/(self.X + self.Y + self.Z)
        self.y = self.Y/(self.X + self.Y + self.Z)
        
        # CIE Chromaticities uv
        #self.u = (0.4661*self.x + 0.1593*self.y)/(self.y - 0.15735*self.x + 0.2424)
        #self.v = (0.6581*self.y)/(self.y - 0.15735*self.x + 0.2424)
        
        # constant for McCamy's/Hernandez-Andrés formula
        n = (self.x - self.x_e)/(self.y - self.y_e)
        
        # Correlated color temperature according to Hernández-Andrés (1999)
        self.color_temp = ( self.A_0 + 
						   self.A_1*np.exp(-n/self.t_1) + 
                           self.A_2*np.exp(-n/self.t_2) + 
                           self.A_3*np.exp(-n/self.t_3) )
        # Correlated color temperature according to McCamy (1992)
        # self.color_temp = 449*(self.n**3) + 3525*(self.n**2) + 6823.3*self.n + 5520.33
        
        # Affichage de la CCT
        self.temp_label.setText("Temperature = "+str(int(round(self.color_temp)))+"K")
        self.temp_label.adjustSize()
    
        # Affichage de l'illuminance (Y)
        self.illuminance_label.setText("Illuminance = " + str(self.Y))
        self.illuminance_label.adjustSize()
    
        
    def calculateHistogram(self):
        """ Calculate the histogram of the input picture.
        """
        
        # Define color map
        colors = [ (255,0,0),(0,255,0),(0,0,255) ]
        # Define empty image to plot histogram in
        plot_to_fill = np.zeros((300,300,3))
        # Define bins of the histogram
        bins = np.arange(256).reshape(256,1)
        
        # Boucle sur les canaux
        for channel, color in enumerate(colors):
            # Calcul de l'histogramme
            hist_item = cv2.calcHist(self.frame,[channel],None,[256],[0,256])
            # Normalisation
            cv2.normalize(hist_item,hist_item,0,255,cv2.NORM_MINMAX)
            # Conversion
            hist = np.int32(np.around(hist_item))
            pts = np.int32(np.column_stack((bins, hist)))
            cv2.polylines(plot_to_fill, [pts], False, color)
        # Mettre dans le bon sens
        histplot = np.flipud(plot_to_fill)
        histplot = np.uint8(histplot)
        
        # Conversion en objet QPixelMap
        self.histplot_qpix = self.convertToQPixelmap(histplot)
            
    def convertToQPixelmap(self, imgToConvert):
        """ Convert cv2 image (BGR numpy array) to QPixelmap object to display
        it the GUI.
        """
        
        # Conversion en image QImage
        frame_qimg = QtGui.QImage(imgToConvert.data, 
                                    imgToConvert.shape[1], 
                                    imgToConvert.shape[0],
                                    imgToConvert.strides[0],
                                    QtGui.QImage.Format_RGB888)
        
        # Conversion en image QPixmap pour l'afficher
        return QtGui.QPixmap.fromImage(frame_qimg)
        
    def savePicture(self):
        """ Save last frame as png picture.
        """
        self.file_name = QtGui.QFileDialog.getSaveFileName(self, 
                                        "Save as... (specify extension)", "")
        cv2.imwrite(self.file_name, self.frame)
        
    def printToUser(self, message):
        """ Print message in a box.
        """
        
        self.messages_to_user.setText(message)
        self.messages_to_user.adjustSize()
        
        
###############################################################################

# Utilisation en dehors de Spyder

def main():
    qtapp = QtGui.QApplication(sys.argv)
    gui = WebcamGui()
    sys.exit(qtapp.exec_())
    
if __name__ == '__main__':
    main() 
    
