from upemtk import *
from random import randint
import os
from time import sleep


def coin_bas(i, j, k, lb, hb):
	"""
	Cette fonction calcule les coordonnées, en pixels, du coin le plus bas 
	d'un bloc représenté par le triplet (i, j, k), où i est le numéro de 
	ligne et j le numéro de colonne de la case sur laquelle est posé le bloc, 
	et k est sa hauteur. Elle reçoit également les dimensions lb et hb d'un 
	bloc. 
	"""

	x = taille_fenetre//2 + (j-i) * lb
	y = taille_fenetre//2 + (j+i) * lb//2 - (k-1) * hb + lb
	return x, y


def affiche_bloc(i, j, k, lb, hb, c="white", cg="grey", cd="lightgrey"):
	"""
	Cette fonction affiche le bloc de coordonnées (i, j, k) conformément au 
	schéma donné dans le sujet. Elle reçoit également les dimensions lb et hb 
	d'un bloc, la taille n du plateau ainsi qu'un paramètre optionnel c 
	indiquant la couleur de la face supérieure du bloc. 
	"""

	# calcul des coordonnées du coin bas du bloc
	x, y = coin_bas(i, j, k, lb, hb)
	# calcul des coordonnées des autres sommets inférieurs du bloc
	xg, xd, ymb = x - lb, x + lb, y - lb//2
	# calcul des ordonnées des sommets supérieurs
	ybh, ymh, yhh = y - hb, y - lb//2 - hb, y - lb - hb

	# dessin de la face supérieure, en vert si c'est l'arrivée
	face_haut = [(x, ybh), (xd, ymh), (x,  yhh), (xg, ymh)]
	polygone(face_haut, remplissage=c, epaisseur=2)

	# dessin des faces latérales si hauteur non nulle
	if k > 0:
		face_gauche = [(x, y),   (xg, ymb), (xg, ymh), (x,  ybh)]
		face_droite = [(x, y),   (xd, ymb), (xd, ymh), (x,  ybh)]
		polygone(face_gauche, remplissage=cg)
		polygone(face_droite, remplissage=cd)


def affiche_bille(i, j, k, lb, hb, n):
	"""
	Cette fonction affiche la bille aux coordonnées (i, j, k). Elle reçoit 
	également les dimensions lb et hb d'un bloc ainsi que la taille n du 
	plateau. 
	"""

	# dessin de la bille proprement dite
	x, y = coin_bas(i, j, k, lb, hb)
	cercle(x, y - 2*lb//3, lb//3, couleur="red", remplissage="red")

	# repère vertical pour une meilleure visibilité
	ligne(x, y - 2*lb//3, x, 20, couleur='red')

	# flèche-repère de gauche
	x, y = coin_bas(n-1, j-0.5, 1, lb, hb)
	fleche(x - 20, y + 20, x - 10, y + 10, couleur="red", epaisseur=3)

	# flèche-repère  de droite
	x, y = coin_bas(i-0.5, n-1, 1, lb, hb)
	fleche(x + 20, y + 20, x + 10, y + 10, couleur="red", epaisseur=3)



###########################
#  FONCTIONS POUR LE JEU  #
###########################

def lancer_jeu(fichier):
	return jeu(fichier)


#créée la matrice du niveau
def fabrication_matrice(fichier):
	niveau = open(fichier, 'r')
	ligne = niveau.readline()

	#hauteur max
	maxi = None

	#la matrice du niveau
	matrice = []
	while ligne != '':
		lst = []
		for elem in ligne:
			if elem != '\n' and elem != ' ':
				if maxi == None:
					maxi = int(elem)
				if maxi < int(elem):
					maxi = int(elem)
				lst.append(int(elem))
		matrice.append(lst)
		ligne = niveau.readline()
	niveau.close()
	return [matrice, maxi]


#regroupe le jeu et ses fonctionnalités
def jeu(fichier):
	#coords matrice
	matrice, maxi = fabrication_matrice(fichier)
	
	#coords de la bille par défaut
	bille = [0, 0, matrice[0][0]+1]

	#paramètre pour connaitre la rotation de la map
	cote = 0

	# "elem" pour récupérer 'lb', 'hb' et le bloc d'arrivée
	deb_aff = True
	elem = affiche_map(matrice, bille, maxi, cote, deb_aff, 0, 0)
	arrivee = elem[0]

	#dictionnaires mémorisants les matrices et les coords de la bille à chaque modification de bille ou de matrice
	#le compteur correspond au nombre à chaque modification
	copie_matrice = copie(matrice)
	dico_matrice, dico_bille = {0: copie_matrice}, {0: bille*1}
	compteur = 1
	deb_aff = False
	x_clic, y_clic = None, None

	while bille != arrivee:
		#récupère la touche
		touche = appui_touche()

		#récupère les coords de la bille et garde la hauteur de sa position
		x, y, z = bille[0], bille[1], bille[2]
		hauteur_precedent = bille[2]

		#fermer le jeu
		if touche == 'q' or touche == 'Q':
			ferme_fenetre()
		#echap pour pause
		elif touche == 'Escape':
			if pause_echap() == 0:
				return touche
		#annuler la dernière action
		elif touche == 'a' or touche == 'A':
			matrice, bille, compteur = revenir_en_arriere(dico_bille, dico_matrice, compteur-1)
		#recommencer la partie
		elif touche == 'r' or touche == 'R':
			matrice, bille, compteur = dico_matrice[0], dico_bille[0], 0
			dico_bille = {0: bille*1}
			dico_matrice = {0: copie(matrice)}
			cote = 0

		#niveau suivante
		elif touche == 'n' or touche == 'N':
			return 1
		#niveau précédente
		elif touche == 'p' or touche == 'P':
			return -1

		#tourner du côté droit
		elif touche == 'd' or touche == 'D':
			if cote < 3:
				cote+=1
			elif cote >= 3:
				cote = 0
		#tourner du côté gauche
		elif touche == 'g' or touche == 'G':
			if cote > -3:
				cote-=1
			elif cote <= -3:
				cote = 0
		#récupère les coords lors du clic
		elif type(touche[0]) == int and type(touche[1]) == int:
			x_clic, y_clic = touche

		else:
			#converti la touche en fonction de la rotation actuelle
			#si rotation à droite
			if cote > 0:
				#l'ordre des rotations des directions
				ordre_direction = ["Left", "Down", "Right", "Up"]
				if touche in ordre_direction:
					i = 0
					while touche != ordre_direction[i]:
						i+=1
					nb = 0
					#la direction est changée autant de fois que le nombre de rotations
					while nb < cote:
						if i == len(ordre_direction)-1:
							i = 0
							touche = ordre_direction[i]
						else:
							i+=1
							touche = ordre_direction[i]
						nb+=1

			#si rotation à gauche (mêmes commentaires que la rotation à droite)
			elif cote < 0:
				ordre_direction = ["Right", "Down", "Left", "Up"]
				if touche in ordre_direction:
					i = 0
					while touche != ordre_direction[i]:
						i+=1
					nb = 0
					while nb > cote:
						if i == len(ordre_direction)-1:
							i = 0
							touche = ordre_direction[i]
						else:
							i+=1
							touche = ordre_direction[i]
						nb-=1

			#modifie les coords de la bille ou des blocs à chaque déplacement
			matrice, bille, x, y = directions(copie(matrice), bille*1, x, y, touche)

		#mémorise modification dans les dictionnaires
		#évite également de mémoriser en double (ou plus) les mêmes coords à la suite
		compteur = pas_double_coords(dico_bille, dico_matrice, compteur, bille, matrice, copie_matrice)

		#réafficher la map avec les déplacements
		efface_tout()
		#s'il n'y a pas eu de clic
		if (x_clic, y_clic) == (None, None):
			affiche_map(matrice, bille, maxi, cote, deb_aff, 0, 0)
		#s'il y a eu un clic
		else:
			affiche_map(matrice, bille, maxi, cote, deb_aff, x_clic, y_clic)
			x_clic, y_clic = None, None
	return None


def copie(matrice):
	lst = []
	for liste in matrice:
		lst.append(liste*1)
	return lst


#récupère la touche
def appui_touche():
	while True:
		evenement = donne_evenement()
		type_ev = type_evenement(evenement)
		if type_ev == 'Touche':
			return touche(evenement)
		elif type_ev == 'ClicGauche':
			return clic_x(evenement), clic_y(evenement)
		mise_a_jour()



#########################
#  AFFICHAGE DU NIVEAU  #
#########################

#affiche les blocs et la bille
def affiche_map(matrice, coords_bille, maxi, cote, debut_affichage, x_clic, y_clic):
	lb = 280/len(matrice)
	hb = min(1.5*lb, 230/(maxi+1))
	#fond d'affichage
	fond_decran()

	#coords de la case d'arrivée
	fin_match = [len(matrice)-1, len(matrice)-1, matrice[-1][-1]+1]
	x_fin, y_fin = len(matrice)-1, len(matrice)-1

	#matrice et bille pour l'affichage avec rotation
	matrice_tempo = copie(matrice)
	x, y, haut = coords_bille[0], coords_bille[1], coords_bille[2]
	bille_tempo = [x, y, haut]

	#les rotations
	i = 0
	#rotation droite
	#la matrice est modifiée pour faire comme si la matrice a fait une rotation
	if cote > 0:
		#en fonction du nombre de rotations à droite
		while i < cote:
			fin = []
			for a in range(len(matrice_tempo)):
				lst = []
				for b in range(len(matrice_tempo[a])):
					lst.append(matrice_tempo[-b-1][a])
				fin.append(lst)
			if len(fin) != 0:
				matrice_tempo = fin

			#rotation pour la bille
			tempo = x
			x = y
			y = (len(matrice_tempo)-1)-tempo
			haut = matrice_tempo[x][y]+1

			#rotation de la case d'arrivée
			fin_tempo = x_fin
			x_fin = y_fin
			y_fin = (len(matrice_tempo)-1)-fin_tempo

			i+=1

	#rotation gauche
	elif cote < 0:
		#en fonction du nombre de rotations à gauche
		while i < -cote:
			fin = []
			for a in range(len(matrice_tempo)):
				lst = []
				for b in range(len(matrice_tempo[a])):
					lst.append(matrice_tempo[b][-a-1])
				fin.append(lst)
			if len(fin) != 0:
				matrice_tempo = fin

			#rotation pour la bille
			tempo = y
			y = x
			x = (len(matrice_tempo)-1)-tempo
			haut = matrice_tempo[x][y]+1

			#rotation de la case d'arrivée
			fin_tempo = y_fin
			y_fin = x_fin
			x_fin = (len(matrice_tempo)-1)-fin_tempo

			i+=1
	bille_tempo = [x, y, haut]

	#affichage de la map
	for ligne in range(len(matrice_tempo)):
		for colonne in range(len(matrice_tempo[ligne])):
			for i in range(matrice_tempo[ligne][colonne]+1):
				#afficher premièrement les blocs derrière la bille, puis la bille, et enfin les blocs devant la bille

				#si les coords du bloc correspondent aux coords de la bille, la bille est aussi dessinée
				#cas où la bille est sur CE bloc
				if (ligne, colonne) == (bille_tempo[0], bille_tempo[1]):
					#si la bille est sur le bloc d'arrivée
					if (ligne, colonne) == (x_fin, y_fin):
						affiche_bloc(ligne, colonne, i, lb, hb, "#a6a6a6", "#595959", "#808080")
					#sinon bloc normal
					else:
						affiche_bloc(ligne, colonne, i, lb, hb, "#009900", "#804000", "#cc6600")
					affiche_bille(bille_tempo[0], bille_tempo[1], bille_tempo[2], lb, hb, len(matrice_tempo))

				#bloc vert d'arrivée
				elif (ligne, colonne) == (x_fin, y_fin):
					affiche_bloc(ligne, colonne, i, lb, hb, "#a6a6a6", "#595959", "#808080")
				#autres blocs
				else:
					affiche_bloc(ligne, colonne, i, lb, hb, "#00ff00", "#804000", "#cc6600")

				#uniquement pour avoir une "animation" d'affichage des blocs lors du lancement d'un niveau
				if debut_affichage == True:
					sleep(0.006)
					mise_a_jour()

	#affichage texte touches
	info = ["R : restart", "A : cancel", "P : previous", "N : next", "G : left view", "D : right view", "Ech : pause", "Q : ragequit"]
	#bouton d'affichage de l'aide pour les touches
	if help(x_clic, y_clic):
		efface("controls")
		cadre_touche(info)
		t_cara = taille_fenetre//45
		for elem_info in range(len(info)):
			texte(taille_fenetre-4, elem_info*((taille_fenetre//10)//2.8), info[elem_info], ancrage="ne", taille=t_cara)

	return fin_match, lb, hb


#affichage du fond d'ecran
def fond_decran():
	lst = ['#3399FF', '#3091FA', '#2E8AF5', '#2B82F0', '#297AEB', '#2673E6', '#246BE0', '#2163DB', 
	'#1F5CD6', '#1C54D1', '#1A4CCC', '#1745C7', '#143DC2', '#1236BD', 
	'#0F2EB8', '#0D26B2', '#0A1FAD', '#0817A8', '#050FA3', '#03089E']
	i = 0
	for c in range(len(lst)):
		rectangle(0, i, taille_fenetre, i+(taille_fenetre//10)//2, couleur=lst[c], remplissage=lst[c])
		i+=(taille_fenetre//10)//2



##################
#  DEPLACEMENTS  #
##################

#fonction qui permet de faire un déplacement en modifiant les coords, que ce soit la bille ou un bloc
def directions(matrice, bille, x, y, touche):
	#condition bordure et touche
	if touche == 'Right' and  y+1 < len(matrice[x]):
		#condition hauteur pour la bille
		if matrice[x][y+1]+1 <= bille[2]:
			y+=1
			bille[0], bille[1], bille[2] = x, y, matrice[x][y]+1

		#condition hauteur et bordure pour pousser un bloc + éviter que le bloc ne soit poussé sur la case d'arrivée
		elif y+1 <= len(matrice[x]) and matrice[x][y+1] == bille[2]:
			if y+2 < len(matrice[x]) and matrice[x][y+1] > matrice[x][y+2] and  (x, y+2, matrice[x][y+2]) != (len(matrice)-1, len(matrice)-1, matrice[-1][-1]):
				matrice[x][y+1]-=1
				matrice[x][y+2]+=1
				bille[0], bille[1], bille[2] = x, y, matrice[x][y]+1

	#les 3 suivants ont les mêmes conditions que précédemment en changeant la direction
	elif touche == 'Left' and  y-1 >= 0:
		if matrice[x][y-1]+1 <= bille[2]:
			y-=1
			bille[0], bille[1], bille[2] = x, y, matrice[x][y]+1

		elif y-1 > 0 and matrice[x][y-1] == bille[2]:
			if y-1 > 0 and matrice[x][y-1] > matrice[x][y-2] and (x, y-2, matrice[x][y-2]) != (len(matrice)-1, len(matrice)-1, matrice[-1][-1]):
				matrice[x][y-1]-=1
				matrice[x][y-2]+=1
				bille[0], bille[1], bille[2] = x, y, matrice[x][y]+1

	elif touche == 'Down' and x+1 < len(matrice):
		if matrice[x+1][y]+1 <= bille[2]:
			x+=1
			bille[0],bille[1],bille[2] = x, y, matrice[x][y]+1

		elif x+1 <= len(matrice) and matrice[x+1][y] == bille[2]:
			if x+2 < len(matrice) and matrice[x+1][y] > matrice[x+2][y] and (x+2, y, matrice[x+2][y]) != (len(matrice)-1, len(matrice)-1, matrice[-1][-1]):
				matrice[x+1][y]-=1
				matrice[x+2][y]+=1
				bille[0], bille[1], bille[2] = x, y, matrice[x][y]+1

	elif touche == 'Up' and x-1 >= 0:
		if matrice[x-1][y]+1 <= bille[2]:
			x-=1
			bille[0], bille[1], bille[2] = x, y, matrice[x][y]+1

		elif x-1 > 0 and matrice[x-1][y] == bille[2]:
			if x-1 > 0 and matrice[x-1][y] > matrice[x-2][y] and (x-2, y, matrice[x-2][y]) != (len(matrice)-1, len(matrice)-1, matrice[-1][-1]):
				matrice[x-1][y]-=1
				matrice[x-2][y]+=1
				bille[0], bille[1], bille[2] = x, y, matrice[x][y]+1

	return matrice, bille, y, x


def revenir_en_arriere(dico_bille, dico_matrice, compteur):
	#lorsque la bille a été déplacée au moins une fois
	if compteur > 0:
		matrice, bille = dico_matrice[compteur-1], dico_bille[compteur-1]
		del dico_matrice[compteur]
		del dico_bille[compteur]
		return matrice, bille, compteur-1

	#lorsqu'il n'y a pas eu de modification
	elif compteur == 0:
		return dico_matrice[compteur], dico_bille[compteur], 1


#fonction qui mémorise dans des dictionnaires la matrice et la bille à chaque modification du jeu
#permet également d'éviter de mémoriser en double (ou plus) les mêmes coords à la suite
def pas_double_coords(dico_bille, dico_matrice, compteur, bille, matrice, copie_matrice):
	if compteur >= 1:
		if not(dico_bille[compteur-1] == bille*1 and dico_matrice[compteur-1] == copie(matrice)):
			dico_bille[compteur], dico_matrice[compteur] = bille*1, copie(matrice)
			compteur+=1
			return compteur

	dico_bille[0], dico_matrice[0] = [0, 0, matrice[0][0]+1]*1, copie(copie_matrice)
	if compteur == 0:
		return 1
	return compteur



#############
#  SOLVEUR  #
#############

#converti en tuples
def vers_tuple(liste_de_listes):
	return tuple(tuple(ligne) for ligne in liste_de_listes)

def vers_tuple_bille(bille):
	return tuple(bille)

#solveur
def solveur_optim(matrice, bille, mon_set, x = None, y = None, ma_route = 'Right'):
	return (solveur(matrice, bille, mon_set, x, y, 'Right') or
		solveur(matrice, bille, mon_set, x, y, 'Left') or
		solveur(matrice, bille, mon_set, x, y, 'Down') or
		solveur(matrice, bille, mon_set, x, y, 'Up'))

def solveur(matrice, bille, mon_set, t_matrice = None, t_bille = None, ma_route = None):
	x, y, la_hauteur = bille

	matrice, bille, x, y = directions(copie(matrice), bille*1, x, y, ma_route)
	t_matrice, t_bille = vers_tuple(matrice), vers_tuple_bille(bille)
	route1, route2, route3 = possibles_directions(ma_route)

	#si un chemin trouvé / condition d'arrêt
	if bille == [len(matrice)-1, len(matrice)-1, matrice[-1][-1]+1]:
		return True

	#récursivement, la fonction vérifie les chemins possibles
	elif (t_matrice, t_bille) not in mon_set and not(bille[2] < matrice[-1][-1]+1):
		#coords à chaque déplacement dans set
		mon_set.add((t_matrice, t_bille))
		return (solveur(matrice, bille, mon_set, t_matrice, t_bille, ma_route) or 
			solveur(matrice, bille, mon_set, t_matrice, t_bille, route1) or 
			solveur(matrice, bille, mon_set, t_matrice, t_bille, route2) or 
			solveur(matrice, bille, mon_set, t_matrice, t_bille, route3))

	#si aucun chemin trouvé
	else:
		return False

def possibles_directions(direction):
	m = ['Left', 'Right', 'Down', 'Up']
	p = []
	for elem in m:
		if elem != direction:
			p.append(elem)
	return p



##########################
#  GENERATION ALEATOIRE  #
##########################

#vérification d'un niveau grâce au solveur
def verification(fichier):
	matrice = fabrication_matrice(fichier)[0]
	bille = [0, 0, matrice[0][0]+1]
	return solveur_optim(matrice, bille, set())

#génère un niveau aléatoire
def levels(nombre):
	level = open("maps_aleatoire/alealevel"+str(nombre)+".txt", 'w')
	name = "alealevel"+str(nombre)+".txt" 
	for c in range(nombre):
		for x in range(nombre):
			if nombre <= 5:
				level.write(str(randint(0, nombre))+' ')
			else:
				level.write(str(randint(0, 6))+' ')
		level.write('\n')
	level.close()
	return name

#les niveaux sont créés et vérifiés dans cette fonction
#si le niveau est faisable, il est enregistré dans une liste
def levels_optim(lst, nb):
	x = 0
	#8 niveaux, est le max
	#7 ou 6 niveaux, est préférable à 8
	for c in range(nb):
		m = c+2
		p = levels(m)
		while verification("maps_aleatoire/"+p) == False:
			p = levels(m)
		lst.append(p)
	return lst



##########
#  MENU  #
##########

#récupère les coords d'un clic
def clic_menu():
	while True:
		evenement = donne_evenement()
		type_ev = type_evenement(evenement)
		if type_ev == 'ClicGauche':
			return clic_x(evenement), clic_y(evenement)
		mise_a_jour()

#création d'un bouton
def boutons_menu(chaine, x, y):
	caractere = (taille_fenetre//10)//2

	rectangle(x - (caractere*7)+5, y - (caractere*1.5)+5, x + (caractere*7)+5, y + (caractere*1.5)+5, couleur="#1a1a1a", remplissage="grey")
	rectangle(x - (caractere*7), y - (caractere*1.5), x + (caractere*7), y + (caractere*1.5), remplissage="white")
	texte(x, y, chaine, ancrage="center", police="Arial", taille=caractere)
	return x - (caractere*7), y - (caractere*1.5), x + (caractere*7), y + (caractere*1.5)


def affiche_menu(menu):
	valeur = False
	FENETRE = taille_fenetre

	#coords des textes
	x_jouer, y_jouer = FENETRE//2, FENETRE//2
	x_quitter, y_quitter = FENETRE//2, y_jouer + ((FENETRE//10)*2.5)
	x_predef, y_predef = FENETRE//2, (FENETRE//2) - (FENETRE//10)
	x_alea, y_alea = FENETRE//2, y_predef + ((FENETRE//10)*2)
	x_retour, y_retour = FENETRE//2, y_alea + ((FENETRE//10)*2)

	#création des boutons en fonction du menu
	if menu == 0:
		fond_decran()
		# TEXTE INFORMATIF
		cadre_pushit()
		#boutons
		ax_jouer, ay_jouer, bx_jouer, by_jouer = boutons_menu("JOUER", x_jouer, y_jouer)
		ax_quitter, ay_quitter, bx_quitter, by_quitter = boutons_menu("QUITTER", x_quitter, y_quitter)

	elif menu == 1:
		fond_decran()
		# TEXTE INFORMATIF ET SON CADRE
		cadre_info("Sélectionnez le mode de jeu")
		#boutons
		ax_predef, ay_predef, bx_predef, by_predef = boutons_menu("Niveaux prédéfinis", x_predef, y_predef)
		ax_alea, ay_alea, bx_alea, by_alea = boutons_menu("Mode aléatoire", x_alea, y_alea)
		ax_retour, ay_retour, bx_retour, by_retour = boutons_menu("Retour", x_retour, y_retour)

	while True:
		x_clic, y_clic = clic_menu()
		if menu == 0:
			#quitter le jeu
			if ax_quitter < x_clic < bx_quitter and ay_quitter < y_clic < by_quitter:
				ferme_fenetre()
			#jouer
			elif ax_jouer < x_clic < bx_jouer and ay_jouer < y_clic < by_jouer:
				return 1

		elif menu == 1:
			if ax_predef < x_clic < bx_predef and ay_predef < y_clic < by_predef:
				return "defini"
			elif ax_alea < x_clic < bx_alea and ay_alea < y_clic < by_alea:
				return "alea"
			elif ax_retour < x_clic < bx_retour and ay_retour < y_clic < by_retour:
				return 0


def boutons_niveau(chaine, x, y):
	caractere = (taille_fenetre//10)//2

	rectangle(x - (caractere*4)+3, y - caractere+5, x + (caractere*4)+3, y + caractere+5, couleur="#1a1a1a", remplissage="grey")
	rectangle(x - (caractere*4), y - caractere, x + (caractere*4), y + caractere, remplissage="white")
	texte(x, y, chaine, ancrage="center", police="Arial", taille=caractere)
	return (x - (caractere*4), y - caractere, x + (caractere*4), y + caractere)

#sélection du nombre de niveaux
def choix_niveau():
	cadre_info("Nombre de niveaux")
	#dictionnaire mémorisant les coords des boutons créés
	dico = {}
	x = taille_fenetre//3 - (taille_fenetre//10)//2
	y = taille_fenetre//2 - taille_fenetre//10
	#création des boutons de 1 à 6
	for nb in range(1, 7):
		if nb == 1:
			tuple_coords = boutons_niveau(str(nb)+" niveau", x, y)
		else:
			tuple_coords = boutons_niveau(str(nb)+" niveaux", x, y)
		#pour afficher les boutons de 1 à 3 à gauche, et de 4 à 6 à droite
		if nb == 3:
			x = ((2*taille_fenetre)//3) + (taille_fenetre//10)//2
			y = taille_fenetre//2 - taille_fenetre//10
		else:
			y+=(taille_fenetre//10)*1.5
		dico[nb] = tuple_coords
	#action supplémentaire pour avoir le bouton retour
	dico["retour"] = boutons_niveau("Retour", taille_fenetre//2, y)
	while True:
		x_clic, y_clic = clic_menu()
		for key in dico:
			if dico[key][0] < x_clic < dico[key][2] and dico[key][1] < y_clic < dico[key][3]:
				return key


def menu_valeur():
	#en fonction de la valeur, on détermine à quelle partie du menu elle correspond
	# 0 : menu principal
	# 1 : menu pour choisir le mode de jeu
	valeur = affiche_menu(0)
	#tant que rien n'est retourné le joueur reste dans le menu
	while True:
		while valeur == 0 or valeur == 1:
			valeur = affiche_menu(valeur)
		# 2 : lance le jeu avec les niveaux prédéfinis
		if valeur == "defini":
			lst = []
			lst = os.listdir("maps/")
			return lst
		# 3 : les niveaux aléatoires
		elif valeur == "alea":
			efface_tout()
			fond_decran()
			nb = choix_niveau()
			if nb == "retour":
				valeur = 1
			else:
				lst = []
				lst = levels_optim(lst, nb)
				return lst


#en jeu
def pause_echap():
	fond_decran()
	cadre_info("Le jeu est en pause")

	#coords des textes + affichage des boutons
	x_reprendre, y_reprendre = taille_fenetre//2, (taille_fenetre//2) - (taille_fenetre//10)
	x_menu, y_menu = taille_fenetre//2, y_reprendre + ((taille_fenetre//10)*2.2)
	x_quitter, y_quitter = taille_fenetre//2, y_menu + ((taille_fenetre//10)*2.2)
	ax_reprendre, ay_reprendre, bx_reprendre, by_reprendre = boutons_menu("Reprendre", x_reprendre, y_reprendre)
	ax_menu, ay_menu, bx_menu, by_menu = boutons_menu("Revenir au menu", x_menu, y_menu)
	ax_quitter, ay_quitter, bx_quitter, by_quitter = boutons_menu("Quitter", x_quitter, y_quitter)
	while True:
		x_clic, y_clic = clic_menu()
		if ax_reprendre < x_clic < bx_reprendre and ay_reprendre < y_clic < by_reprendre:
			return None
		elif ax_menu < x_clic < bx_menu and ay_menu < y_clic < by_menu:
			return 0
		elif ax_quitter < x_clic < bx_quitter and ay_quitter < y_clic < by_quitter:
			ferme_fenetre()

#bouton d'affichage de l'aide pour les touches
def help(x_clic, y_clic):
	t_cara = taille_fenetre//45
	ax, bx = taille_fenetre - t_cara*8, taille_fenetre-5
	ay, by = 5, (taille_fenetre//10)//2
	rectangle(ax, ay, bx, by, couleur="#002e4d", remplissage="#66ccff", epaisseur=3, tag="controls")
	texte((ax+bx)//2, (ay+by)//2, "Contrôles", ancrage="center", taille=t_cara, tag="controls")
	if ax < x_clic < bx and ay < y_clic < by:
		return True
	else:
		return False



######                            ######
## L'AFFICHAGE DES TEXTES INFORMATIFS ##
######                            ######

def cadre_pushit():
	FENETRE = taille_fenetre
	taille_pushit = (FENETRE//10)-5
	texte(FENETRE//2+2, FENETRE//5.3+2, "Push it DOWN !", ancrage="center", police="Impact", taille=taille_pushit)
	texte(FENETRE//2, FENETRE//5.3, "Push it DOWN !", couleur="white", ancrage="center", police="Impact", taille=taille_pushit)

def cadre_info(chaine):
	FENETRE = taille_fenetre
	abs_texte, ord_texte, t_txt = FENETRE//2, FENETRE//6, (FENETRE//10)//2
	rectangle(abs_texte - (t_txt*9)+5, ord_texte - (t_txt*2)+5, abs_texte + (t_txt*9)+5, ord_texte + (t_txt*2)+5, remplissage="#004d99")
	rectangle(abs_texte - (t_txt*9), ord_texte - (t_txt*2), abs_texte + (t_txt*9), ord_texte + (t_txt*2), remplissage="#66ccff")
	texte(abs_texte + 2, ord_texte + 2, chaine, ancrage="center", police="Arial", taille=t_txt)
	texte(abs_texte, ord_texte, chaine, couleur="white", ancrage="center", police="Arial", taille=t_txt)

def cadre_win():
	FENETRE = taille_fenetre
	grandeur = (FENETRE//10)//2
	rectangle(FENETRE//2 - (grandeur*5)+3, FENETRE//2 - (grandeur*2)+3, FENETRE//2 + (grandeur*5)+3, FENETRE//2 + (grandeur*2)+3, couleur="black", remplissage="black")
	rectangle(FENETRE//2 - (grandeur*5), FENETRE//2 - (grandeur*2), FENETRE//2 + (grandeur*5), FENETRE//2 + (grandeur*2), remplissage="white")
	texte(FENETRE//2+2, FENETRE//2+2, "Gagné !", couleur="grey", ancrage="center", police="Arial", taille=grandeur)
	texte(FENETRE//2, FENETRE//2, "Gagné !", couleur="black", ancrage="center", police="Arial", taille=grandeur)

def cadre_touche(lst):
	rectangle(taille_fenetre - ((taille_fenetre//10)*2)-6, 3, taille_fenetre-5, len(lst)*((taille_fenetre//10)//2.8)+3, couleur="#00264d", remplissage="#00264d")
	rectangle(taille_fenetre - ((taille_fenetre//10)*2)-2, 0, taille_fenetre-1, len(lst)*((taille_fenetre//10)//2.8), couleur="#4da6ff", remplissage="#4da6ff")



########################
#                      #
#  DEBUT DU PROGRAMME  #
#                      #
########################

if __name__ == "__main__":
	taille_fenetre = 600
	cree_fenetre(taille_fenetre, taille_fenetre)

	#le menu
	lst = menu_valeur()

	c = 0
	efface_tout()
	while True:
		#vérification du niveau si c'est un niveau aléatoire ou non
		if "alealevel" in lst[c]:
			niveau = lancer_jeu("maps_aleatoire/"+lst[c])
		else:
			niveau = lancer_jeu("maps/"+lst[c])
		#lorsque le joueur a fini un niveau
		if niveau == None:
			#affichage du panneau "gagné"
			cadre_win()
			
			m = None
			while m not in ('n', 'N', 'p', 'P', 'r', 'R', 'q', 'Q', 'Escape'):
				m = appui_touche()

			if m == 'q' or m == 'Q':
				ferme_fenetre()

			elif m == 'Escape':
				efface_tout()
				if pause_echap() == 0:
					lst, c = menu_valeur(), 0

			efface_tout()
			if c < len(lst)-1:
				if m == 'n' or m == 'N':
					c+=1
			elif c > 0:
				if m == 'p' or m == 'P':
					c-=1

		#si le joueur a choisi de retourner au menu avec pause
		elif niveau == 'Escape':
			efface_tout()
			lst, c = menu_valeur(), 0

		#si le joueur change de niveau en cours de jeu
		else:
			if c != len(lst)-1 or niveau == -1:
				if (c > 0 or niveau == 1):
					c+=niveau
			efface_tout()
