#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 10:30:06 2017

@author: pvkh
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 14:45:07 2017

Creating GUI

@author: pvkh
"""

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
        
        # webcam canvas
        self.img_label = QtGui.QLabel(self)
        
        # histogram canvas
        self.his_label = QtGui.QLabel(self)
        
        # Text boxes
        self.temp_label = QtGui.QLabel(self)
        self.red_label = QtGui.QLabel(self) # hips
        self.green_label = QtGui.QLabel(self)
        self.blue_label = QtGui.QLabel(self)
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
                self.webcam = cv2.VideoCapture(0) # Créer un objet OpenCV
                self.printToUser("Webcam connected.")
        except AttributeError:
            self.webcam = cv2.VideoCapture(0)
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
        self.red_label.setText("Mean RED: "+str(int(round(self.R))))
        self.red_label.adjustSize()
        self.green_label.setText("Mean GREEN: "+str(int(round(self.G))))
        self.green_label.adjustSize()
        self.blue_label.setText("Mean BLUE: "+str(int(round(self.B))))
        self.blue_label.adjustSize()
            
    def calculateTemperature(self):
        """ Calculate mean color temperature.
        """
        
        # CIE space
        X = (-0.14282)*self.R + (1.54924)*self.G + (-0.95641)*self.B
        Y = (-0.32466)*self.R + (1.57837)*self.G + (-0.73191)*self.B
        Z = (-0.68202)*self.R + (0.77073)*self.G + (0.56332)*self.B

        # Chromaticity
        x = X/(X+Y+Z)
        y = Y/(X+Y+Z)
        
         # constant for McCamy's formula
        n = (x - 0.3320) / (0.1858 - y)
        
        # Correlated color temperature according McCamy
        self.color_temp = 449*(n**3) + 3525*(n**2) + 6823.3*n + 5520.33
        
        self.temp_label.setText("Temperature = "+str(int(round(self.color_temp)))+"K")
        self.temp_label.adjustSize()
    
    
        
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
    