# lumi-webcam
Projet informatique en Python pour le module Informatique du M2 LuMI (UPMC)

# Note importante concernant OpenCV
Il semblerait que OpenCV enregistre les images de la webcam non pas en (RGB) mais en (BGR), ie:
     image[:,:,0] = BLUE
     image[:,:,1] = GREEN
     image[:,:,2] = RED


