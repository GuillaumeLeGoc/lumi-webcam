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
        
        ## Création de la fenêtre
        # Layout en grille
        grid_layout = QtGui.QGridLayout()
        # Espace entre les widgets
        grid_layout.setSpacing(10)
        
        ## Création des widgets
        # Boutons
        button_on = QtGui.QPushButton('On', self)
        button_off = QtGui.QPushButton('Off', self)
        button_save = QtGui.QPushButton('Save as picture', self)
        button_start = QtGui.QPushButton('Start stream',self)
        button_stop = QtGui.QPushButton('Stop stream',self)
        
        # Image window
        self.img_label = QtGui.QLabel(self)
                
        # Ajout des widgets
        grid_layout.addWidget(button_on, 1, 0, 2, 2)
        grid_layout.addWidget(button_off, 3, 0, 2, 2)
        grid_layout.addWidget(button_save, 5, 0, 1, 1)
        grid_layout.addWidget(button_start, 6, 0, 1, 1)
        grid_layout.addWidget(button_stop, 7, 0, 1, 1)
        grid_layout.addWidget(self.img_label, 9, 0, 7, 7)
        
        # Ajout du layout sur la fenêtre principale
        self.setLayout(grid_layout)
        
        # Paramètre et affichage de l'interface à l'écran
        self.setGeometry(300, 300, 800, 600) # x, y, W, H; move+resize method
        self.setWindowTitle("Webcam Analyzer") # Titre de la fenêtre  
        
        # Fonctions connectées aux boutons
        button_on.clicked.connect(self.openWebcam)
        button_off.clicked.connect(self.closeWebcam)
        button_start.clicked.connect(self.startStream)
        button_stop.clicked.connect(self.stopStream)
        
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

    def closeWebcam(self):
        """ Close webcam through OpenCV.
        """
        
        try: # Vérifie si l'attribut webcam existe déjà
            if self.webcam.isOpened():
                self.webcam.release()
                print "Webcam disconnected."
            else:
                print "Webcam already disconnected."
        except AttributeError:
            print "Error: Webcam not connected yet."
            
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
            
    def calculateTemperature(self):
        """ Calculate mean color temperature.
        """


gui = WebcamGui()
    
    