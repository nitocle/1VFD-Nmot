Ci-joint le code utilisé pour le pilotage de 3 moteurs avec un seul var.

Architecture 
Le fichier en py thon comporte toutes les instructions
les fichiers text sont des fihciers de paramètres (un fichier par moteur, nommé en Numérodemoteur.txt). Le premier moteur porte le numéro 0, le deuxième le numéro 1, le troisième le nupméro 2...
Le fichier referent.txt comporte les paramétres d'origine (usine). Ce fichier référent est rechargé chaque fois qu'on change de moteur pour éviter tout problème de paramétrage "herité" du précédent moteur.



Les   grandes partie de ce dev sont :
