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
        
        ## Création de la fenêtre
        # Layout en grille
        grid_layout = QtGui.QGridLayout()
        # Espace entre les widgets
        grid_layout.setSpacing(10)
        
        ## Création des widgets
        # Boutons
        button_connect = QtGui.QPushButton('Connect webcam', self)
        button_save = QtGui.QPushButton('Save as picture', self)
        button_start = QtGui.QPushButton('Start stream',self)
        button_stop = QtGui.QPushButton('Stop stream',self)
        
        # Image window
        self.img_label = QtGui.QLabel(self)
        
        # Text boxes
        self.temp_label = QtGui.QLabel(self)
        self.red_label = QtGui.QLabel(self) # hips
        self.green_label = QtGui.QLabel(self)
        self.blue_label = QtGui.QLabel(self)
                
        # Ajout des widgets
        grid_layout.addWidget(button_connect, 1, 0, 2, 2)
        grid_layout.addWidget(button_save, 5, 0, 1, 1)
        grid_layout.addWidget(button_start, 6, 0, 1, 1)
        grid_layout.addWidget(button_stop, 7, 0, 1, 1)
        grid_layout.addWidget(self.img_label, 9, 0, 7, 7)
        grid_layout.addWidget(self.temp_label, 9, 10, 3, 3)
        grid_layout.addWidget(self.red_label, 10, 10, 3, 3)
        grid_layout.addWidget(self.green_label, 11, 10, 3, 3)
        grid_layout.addWidget(self.blue_label, 12, 10, 3, 3)
        
        # Ajout du layout sur la fenêtre principale
        self.setLayout(grid_layout)
        
        # Paramètre et affichage de l'interface à l'écran
        self.setGeometry(300, 300, 800, 600) # x, y, W, H; move+resize method
        self.setWindowTitle("Webcam Analyzer") # Titre de la fenêtre  
        self.setWindowIcon(QtGui.QIcon("webcam-512.png")) # Icone
        
        # Fonctions connectées aux boutons
        button_connect.clicked.connect(self.openWebcam)
        button_start.clicked.connect(self.startStream)
        button_stop.clicked.connect(self.stopStream)
        button_save.clicked.connect(self.savePicture)

        # Afficher le GUI à l'écran
        self.show()
        
    def openWebcam(self):
        """ Open webcam through OpenCV.
        """
    
        try: # Vérifier si l'attribut webcam existe
            if self.webcam.isOpened():
                print "Webcam already connected."
            else:
                self.webcam = cv2.VideoCapture(0) # Créer un objet OpenCV
                print "Webcam connected."
        except AttributeError:
            self.webcam = cv2.VideoCapture(0)
            print "Webcam connected."
       
    def startStream(self):
        """ Begin webcam stream.
        """
        
        try: # Vérifier si l'attribut existe, autrement prévenir l'utilisateur.
            if self.webcam.isOpened(): # vérifie si la camera est bien connectée
                self.isRead, self.webcam_frame = self.webcam.read() # tenter une 
                # première capture
                self.webcam_break_loop = False # initialiser le témoin de on/off
                print "Starting stream."
                while self.isRead: # boucle pour streamer la webcam
                    
                    # Récupère une frame de la webcam                
                    self.isRead, self.frame = self.webcam.read()
                    
                    # Conversion BGR > RGB
                    self.frame_rgb = cv2.cvtColor(self.frame, 
                                                         cv2.COLOR_BGR2RGB)
                    
                    # Calcul de la moyenne des niveaux de R,G,B
                    self.averageRGB()
                    
                    # Calcul et affichage de la température de couleurs
                    self.calculateTemperature()
                    
                    # Conversion de l'image OpenCV en image QImage
                    self.frame_qimg = QtGui.QImage(self.frame_rgb.data, 
                                    self.frame_rgb.shape[1], 
                                    self.frame_rgb.shape[0],
                                    self.frame_rgb.strides[0],
                                    QtGui.QImage.Format_RGB888)
                    
                    # Conversion en image QPixmap pour l'afficher
                    self.frame_qpix = QtGui.QPixmap.fromImage(self.frame_qimg)
                    
                    # Affichage de l'image sur le canvas du GUI
                    self.img_label.setPixmap(self.frame_qpix)
                                                                    
                    cv2.waitKey(20) # laisser le temps d'appuyer sur "stop"
                    if self.webcam_break_loop:
                        print "Streaming stopped."
                        break
            else:
                print "Connect webcam first..."
        except AttributeError:
            print "Connect webcam first."

    def stopStream(self):
        """ Stop webcam stream.
        """
        
        try:
            if not self.webcam_break_loop:
                self.webcam_break_loop = True
                print "Stopping stream."
            else:
                print "Stream not running..."
        except AttributeError:
            print "Stream not running."
            
    def averageRGB(self):
        """Get the mean Red, Green and Blue in webcame frame.
        """
        
        # Calcul des moyennes
        self.R = self.frame_rgb[:,:,0].mean()
        self.G = self.frame_rgb[:,:,1].mean()
        self.B = self.frame_rgb[:,:,2].mean()
        
        # Affichage dans les boxes
        self.red_label.setText(str(self.R))
        self.red_label.adjustSize()
        self.green_label.setText(str(self.G))
        self.green_label.adjustSize()
        self.blue_label.setText(str(self.B))
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
        
        self.temp_label.setText(str(self.color_temp))
        self.temp_label.adjustSize()
        
    def savePicture(self):
        """ Save last frame as png picture.
        """
        self.file_name = QtGui.QFileDialog.getSaveFileName(self, "Save as... (specify extension)", "")
        cv2.imwrite(self.file_name, self.frame)
        
###############################################################################

# Utilisation en dehors de Spyder

def main():
    qtapp = QtGui.QApplication(sys.argv)
    gui = WebcamGui()
    sys.exit(qtapp.exec_())
    
if __name__ == '__main__':
    main() 
    