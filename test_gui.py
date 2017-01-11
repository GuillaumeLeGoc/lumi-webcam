#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 15:56:05 2017

@author: pvkh

Basé sur l'interface graphique créée par Thibaut Jacqmin
"""

from PyQt4 import QtGui

class MonSecondGui(QtGui.QWidget):
    # (Dérive de la classe QtGui.QWidget)
    """ Cette classe gère une interface graphique
        (GUI) contenant un bouton qui lorsqu'il est pressé
        affiche le texte contenu dans une boite de texte
        dans la boite de commande.        
    """
 
    def __init__(self):
        # Commande nécessaire pour éxécuter 
        # la fonction __init__ de la classe
        # parent (Qt.Gui.QWidget)
        super(MonSecondGui, self).__init__()
        
        # Création d'un objet layout de type HBox
        self.main_layout = QtGui.QHBoxLayout()
        
        # Création d'un objet bouton avec un texte
        self.button_print = QtGui.QPushButton('Bouton surprise', self)
        # Ajout du bouton sur le layout main_layout        
        self.main_layout.addWidget(self.button_print)
        
        # Ecriture de texte non modifiable sur le Layout
        self.texte_non_modifiable = QtGui.QLabel('Entrer du texte ici : ')
        self.main_layout.addWidget(self.texte_non_modifiable)
        
        # Création d'une boite de texte modifiable avec 
        # Texte par défaut
        self.texte_modifiable = QtGui.QLineEdit(u'Texte par défaut', self)
        self.main_layout.addWidget(self.texte_modifiable)
     
        # Nécessaire pour dire à Python quel est le layout
        # principal
        self.setLayout(self.main_layout)        
        
        # Affiche le GUI à l'écran        
        self.show()
        
        # Fonction connectée au bouton (fonction appelée lorsque l'on clique
        # sur le bouton)
        self.button_print.clicked.connect(self.print_texte_modifiable)
     
    def print_texte_modifiable(self):
        """
            Fonction appelée lors d'un clic
            sur le bouton. Affiche le texte
            de la boite de texte modifiable dans
            la boite de commande IPYthon
        """
        print self.texte_modifiable.text()
 
m = MonSecondGui()