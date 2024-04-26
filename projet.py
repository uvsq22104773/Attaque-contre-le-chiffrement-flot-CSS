import random

# Classe pour créer un lfsr
class LFSR:
    # Prends en entrée une liste de 0 et de 1 et la position des bits non nuls du coefficient de rétroaction
    def __init__(self, s:list, c_non_nuls:list=[0]):
        self.s = s
        c = [0] * (len(s))
        for elem in c_non_nuls:
            c[(len(s)-1)-elem] = 1
        self.c = c
        self.s_default = s

    # Décale les bits et génère un bit de remplacement grace aux coefficients de rétroaction
    # Retourne le premier bit
    def decalage(self):
        b = 0
        for i in range(len(self.s)):
            b = (b + self.c[i] * self.s[i]) % 2
        s0 = self.s[-1]
        self.s = [b] + self.s[:-1]
        return s0

    # Fais 8 décalages et renvoient les 8 bits renvoyés
    def generer_octet(self):
        octet = []
        for _ in range(8):
            octet = [self.decalage()] + octet
        return octet
    
    # Reinitialise la clé
    def remise_par_default(self):
        self.s = self.s_default

    # Méthode de vérification
    # Pour savoir s'il y a bien 2**(taille du lfsr) configuration
    def verif_random(self):
        # Énumérateur de l'animation de chargement
        anim = animate()
        # On prend la taille du lfsr
        size = len(self.s)
        # On fait une boucle pour générer un s
        while True:
            # Liste pour générer un s aléatoire
            s_random = []
            # Chaine de caractère pour pouvoir mettre tous les chiffres générés
            str_s = ""
            # Génère s avec des 0 ou des 1 aléatoirement de la taille du lfsr
            for i in range(size):
                s_random.append(random.randint(0, 1))
            # Mets tous les chiffres dans la chaine de caractère
            for elem in s_random:
                str_s += str(elem)
            # Si là on n'a pas généré que des 0 on sort de la boucle sinon on recommence
            if str_s != "0"*size:
                break
        # On garde l'ancien s du lfsr pour pouvoir le remettre après
        ancien_s = self.s
        # On met le s générer aléatoirement dans le lfsr
        self.s = s_random
        # Creer un set pour pouvoir mettre toutes les configurations du lfsr dedans
        config = set()
        # Calcule avant pour connaitre la vitesse de l'animation
        calcule = 42500//((size/4)**2)
        # On calcule le nombre max de possibilité pour ne pas à le refaire plusieurs fois
        configuration_possible = (2**size)-1
        # On fait tourner le lfsr 2**(taille du lfsr)-1 qui est le nombre max de configuration possible
        for i in range(configuration_possible):
            # On ajoute la configuration actuelle dans le set
            config.add(str(self.s))
            # On fait tourner le lfsr le nombre de fois qu'il faut pour qu'une nouvelle série soit à l'intérieur
            for j in range(size):
                self.decalage()
            # Calcule pour savoir si on change l'animation de chargement
            if calcule>1 and i%(calcule) == 1:
                next(anim)
                # Si le lfsr est grand on affiche le nombre de calcule qu'on a faits pour le moment
                if size > 18:
                    print(f" ({i}/{configuration_possible})         ", end="")
            elif calcule<1:
                next(anim)
                # Affiche a quel calcul on est
                print(f" ({i}/{configuration_possible})         ", end="")
            # Vérification tous les 100 000 états si pour l'instant il y en a comme attendu
            # pour ne pas à fais des millions de tours pour rien
            if i%100000 == 0:
                if i != len(config)-1:
                    break
            # Et on recommence
        # Réinitialisation affichage animation
        print("\r                                 \r", end="")
        # On regarde si le set contient bien 2**(taille du lfsr)-1 élément
        # Car un set ne peut pas contenir 2 éléments identiques donc si 2 configurations sont identiques
        # Il en manquera au moins un dans le set
        if len(config) == configuration_possible:
            # On remet la configuration du lfsr qu'il y avait avant la vérification
            self.s = ancien_s
            # On retourne vrai
            return True, len(config)
        # S'il manque au moins un élément on retourne faux
        else:
            # On remet la configuration du lfsr qu'il y avait avant la vérification
            self.s = ancien_s
            # On retourne faux
            return False, len(config)

# Classe pour créer un css
class CSS:
    # Il prend en entrée que la clé secrète de 40 bits
    # Et créer grâce à cela les 2 lsfr qui le compose
    def __init__(self, s:list):
        self.lsfr17 = LFSR([1]+s[:16], [14, 0])
        self.lsfr25 = LFSR([1]+s[16:], [12, 4, 3, 0])
        self.c = 0

    # Grâce aux 2 lsfr créé et à la méthode de classe genrer_octet
    # Transforme juste les octets reçus en décimal font le calcul
    # Fais le test pour le c et renvoie z sous forme de liste binaire
    def genere_cle(self):
        x = int(''.join(str(elem) for elem in self.lsfr17.generer_octet()), 2)
        y = int(''.join(str(elem) for elem in self.lsfr25.generer_octet()), 2)
        z = (x + y + self.c) % 256
        self.c = 1 if x + y > 255 else 0
        # Transforme le z qui est un entier en binaire sous forme de liste
        k = [int(elem) for elem in str(bin(z))[2:]]
        # Rajoute un 0 devant pour compléter jusqu'à 8 bits
        while len(k) < 8:
            k = [0] + k
        return k
  
    # Méthode pour chiffre et déchiffrer le message
    def chiffrer_dechiffrer(self, m:list):
        # Compteur pour l'animation de chargement
        compt = 0
        # Générateur pour l'animation de chargement
        anim = animate()
        # Remets la suite binaire du lfsr à l'état initiale pour pouvoir chiffrer ou déchiffrer
        self.lsfr17.remise_par_default()
        self.lsfr25.remise_par_default()
        c = []
        # Chiffre ou déchiffre le message d'octet en octet
        while len(m)>0:
            cle = self.genere_cle()
            for elem, k in zip(m[:8], cle):
                c.append((elem+k)%2)
            m = m[8:]
            # Ajoute 1 au compteur de l'animation
            compt += 1
            # Tous les 2500 exécutions, change l'animation
            if compt%2500 == 1:
                next(anim)
        # Éfface l'affichage de l'animation
        print("\r                \r", end="")
        return c

# Fonction pour l'animation de chargement pendant l'attaque
# Écrit dans le terminal puis attend qu'on lui demande le prochain
# Car c'est un énumérateur
def animate():
    while True:
        # Écrit
        print("\rloading |", end="")
        # Attend qu'on le rappelle
        yield
        # Écrit
        print("\rloading /", end="")
        # Attend qu'on le rappelle
        yield
        # Écrit
        print("\rloading -", end="")
        # Attend qu'on le rappelle
        yield
        # Écrit
        print("\rloading \\", end="")
        # Attend qu'on le rappelle
        yield

# Fonction pour générer un s et 6 z pour le test de l'attaque
def generer_z(alea=True):
    # Créer une liste pour contenir la configuration du css
    s = []
    # Si on veut generer des z avec une initialisation aleatoire
    if alea==True:
    # Créer 40 0 ou 1 aléatoirement
        for i in range(40):
            s.append(random.randint(0,1))
    else:
        s = alea
    # Ligne de test
    # s = [1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0]
    # Creer un css avec le s aléatoire
    css = CSS(s)
    # Création d'une liste pour les 6 premiers z
    z = []
    # On fait tourner le css 6 fois pour avoir les 6 premières clés
    for i in range(6):
        z.append(css.genere_cle())
    # On retourne le s utilisé pour pouvoir comparer la réponse de l'attaque
    # Avec la liste de z pour l'attaque
    return s, z

# Fonction d'attaque d'un css
# Il prend en entrée les 6 premiers z d'un css
def attaque_css(z:list):
    compt = 0
    anim = animate()
    # Il va tester les 2**16 possibilités pour l'initialisation du lfsr17
    for i in range(2**16):
        # Créer une nouvelle liste avec les éléments qui sont sous forme de liste dans z
        # en entier base 10
        z_int = []
        for liste in z:
            z_int.append(int(int(''.join(str(elem) for elem in liste), 2)))
        # Création de l'initialisation x pour le lfsr17
        random_x = [1]
        # Pour le résultat du lfsr17
        x = []
        # Résultat sous forme entière base 10 du lsfr17
        x_int = []
        # pour le résultat du calcule d'y grace à x et z
        y = []
        # Résultat sous forme d'entier
        y_int = []
        # Pour initialiser les css de test pour savoir si les 6 premiers z sont corrects
        s = []
        # On prend les i dans l'ordre pour trouver le x correspondant au lsfr17 du css
        # On le met en base 2 dans une liste car le lfsr prend une liste en entrée
        for elem in str(format(i, '016b')):
            random_x.append(int(elem))
        # Création du lfsr17
        lfsr = LFSR(random_x, [14, 0])
        # Sortie des 3 premiers x
        for j in range(3):
            x = [lfsr.generer_octet()] + x
            x_int = [int(int(''.join(str(elem) for elem in x[0]), 2))] + x_int
        # Calcule du y, c = 1 quand le z-x d'avant < 0, 0 sinon
        c = 0
        for j in range(3):
            y_int.append((z_int[j] - x_int[2-j] - c) % 256)
            # Met c à 1 si z-x < 0 sinon met un 0
            c = 1 if z_int[j] - x_int[2-j] < 0 else 0
            # Ajoute dans la liste y sous forme liste binaire pour pouvoir initialiser le css
            y.append([])
            y = [[]] + y
            for elem in str(format(y_int[j], '08b')):
                y[0].append(int(elem))
        # Création du s avec les 40 bits d'initialisation
        # 2 premiers octets de x
        for j in range(1, 3):
            s += x[j]
        # 3 octets de y calculer précedemment
        for elem in y:
            s += elem
        # Création du css de test
        css = CSS(s)
        z_prime = []
        # Génération des 6 z
        for j in range(6):
            z_prime.append(css.genere_cle())
        # Ajoute un au compteur pour l'animation
        compt += 1
        # Si le compteur a augmenté de 250
        if compt % 250 == 1:
            # Change l'animation
            next(anim)
        # Vérification des z
        # Si les z générés sont les mêmes que les 6 connues alors on arrête la boucle et on renvoie le résultat
        if z_prime == z:
            print("\r                          \r", end="")
            return s
    # Retourne faux si rien trouvé
    return False

# Fonction pour la démonstration dans le terminal
def demo():
    q = ("1", "3", "6")
    y_n = ("y", "n")
    c_d = ("c", "d")
    chiffres = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
    while True:
        question = input("\033[91mA tout moment vous pouvez revenir au menu du début avec 'm' ou arrêtez le programme avec 'exit'.\033[0m\nLa démonstration de quelle question souhaitez-vous ? (1, 3 ou 6)\n")
        if question in q:
            break
        elif question == "m":
            return demo()
        elif question == "exit":
            return
        print("Erreur, réponse attendue : 1, 2, 3 ou 6.")
    
    if question == "1":

        while True:
            taille17 = input("Souhaitez-vous que la taille du LFSR soit de 17 bits ? (y, n)\n")
            if taille17 in y_n:
                break
            elif taille17 == "m":
                return demo()
            elif taille17 == "exit":
                return

        if taille17 == "y":
            taille = 17
        else:

            while True:
                taille = input("Combien de bits souhaitez-vous que le LFSR fasse ? (Un entier attendu)\n")
                if taille == "m":
                    return demo()
                elif taille == "exit":
                    return
                try:
                    taille = int(taille)
                    break
                except:
                    pass
        
        while True:
            coef17 = input("Souhaitez-vous que les coefficients de rétroaction non-nuls soient {14, 0} ? (y, n)\n")
            if coef17 in y_n:
                break
            elif coef17 == "m":
                return demo()
            elif coef17 == "exit":
                return
        
        if coef17 == "y":
            coef = [14, 0]
        else:

            while True:
                n = True
                coef_tmp = input("Quels coefficients de rétroaction non-nuls souhaitez-vous ? (Écrire des nombres entiers séparés par des virgules. Exemple: 12,5,3)\n")
                if coef_tmp == "m":
                    return demo()
                elif coef_tmp == "exit":
                    return
                try:
                    if coef_tmp[-1] in chiffres:
                        coef_tmp += ","
                    coef = []
                    tmp = 0
                    for elem in coef_tmp:
                        if elem in chiffres:
                            tmp = tmp*10 + int(elem)
                        elif elem == ",":
                            if tmp < taille:
                                coef.append(tmp)
                                tmp = 0
                            else:
                                print(f"Coefficient out of range: {tmp}, attendu : <{taille}")
                                n = False
                                break
                        else:
                            n = False
                            break
                    if n:
                        print(coef)
                        break
                except:
                    continue

        lfsr = LFSR([0]*taille, coef)
        reponse, nb = lfsr.verif_random()
        if reponse:
            print(f"Vrai, {nb} valeurs différentes trouvé, ce qui équivaut à 2**{taille}-1 ({(2**taille)-1}) états différents avec comme coeficients de rétrocaction {coef}.")
        else:
            print(f"Faux, {nb} valeurs différentes trouvé, ce qui n'équivaut pas à 2**{taille}-1 états différents avec comme coeficients de rétrocaction {coef}.")
    elif question == "3":

        while True:
            chiffre = input("Voulez-vous chiffrer (c) ou déchiffrer (d) un nombre ? (c, d)\n")
            if chiffre in c_d:
                break
            elif chiffre == "m":
                return demo()
            elif chiffre == "exit":
                return
        
        if chiffre == "c":
            action1 = "chiffré"
            action2 = "chiffrer"
        else:
            action1 = "déchiffré"
            action2 = "déchiffrer"

        while True:
            if chiffre == "c":
                message_chiffre = input("Souhaitez-vous chiffrer 0xffffffffff ? (y, n)\n")
            else:
                message_chiffre = input("Souhaitez-vous déchiffrer 0xffffb66c39 ? (y, n)\n")
            if message_chiffre in y_n:
                break
            elif message_chiffre == "m":
                return demo()
            elif message_chiffre == "exit":
                return
            
        if message_chiffre == "y":
            if chiffre == "c":
                message = "0xffffffffff"
            else:
                message = "0xffffb66c39"
        else:

            while True:
                message = input(f"Quel hexadécimal souhaitez-vous {action2} ? (Un nombre de la forme 0xf1ab94e30a attendu)\n")
                if message == "m":
                    return demo()
                elif message == "exit":
                    return
                try:
                    message = hex(int(message, 16))
                    break
                except:
                    continue
            
        message = int(message, 16)
        m = []
        for elem in str(bin(message))[2:]:
            m.append(int(elem))
        
        while True:
            initia_css = input("Souhaitez-vous que le CSS soit initialisé à 0x0 ? (y, n)\n")
            if initia_css in y_n:
                break
            elif initia_css == "m":
                return demo()
            elif initia_css == "exit":
                return
            
        if initia_css == "y":
            s = [0]*40
        else:

            while True:
                initia = input("Quel initialisation souhaitez-vous ? (Hexadécimal avec 10 chiffres maximem est attendu. Exemple: 0xffffffffff)\n")
                if initia == "m":
                    return demo()
                elif initia == "exit":
                    return
                try:
                    initia = hex(int(initia, 16))
                    if len(initia[2:]) <= 10:
                        break
                    else:
                        continue
                except:
                    continue
                
            initia = int(initia, 16)
            s = []
            for elem in str(bin(initia))[2:]:
                s.append(int(elem))
            for i in range(40-len(s)):
                s = [0] + s
            
        css = CSS(s)
        m_chiffre = css.chiffrer_dechiffrer(m)
        m = hex(int(''.join(str(elem) for elem in m), 2))
        m_chiffre = hex(int(''.join(str(elem) for elem in m_chiffre), 2))
        print(f"{m_chiffre} est le {action1} de {m}.")
    elif question == "6":

        while True:
            alea = input("Souhaitez-vous initialiser le CSS aléatoirement ? (y, n)\n")
            if alea in y_n:
                break
            elif alea == "m":
                return demo()
            elif alea == "exit":
                return

        if alea == "y":
            s, z = generer_z()       
        else:

            while True:
                entree = input("Avec quelles valeurs souhaitez-vous l'initialiser ? (En nombre hexadécimal. Exemple: 0xffffffffff)\n")
                if entree == "m":
                    return demo()
                elif entree == "exit":
                    return
                try:
                    entree = hex(int(s, 16))
                    if len(entree[2:]) <= 10:
                        break
                    else:
                        continue
                except:
                    continue

            s = []
            for elem in str(bin(entree))[2:]:
                s.append(int(elem))
            for i in range(40-len(s)):
                s = [0] + s
            s, z = generer_z(s)
        s_attaque = attaque_css(z)
        if s_attaque != False:
            s = hex(int(''.join(str(elem) for elem in s), 2))
            s_attaque = hex(int(''.join(str(elem) for elem in s_attaque), 2))
            print(f"L'initialisation dans le générateur était: {s}.\nEt l'attaque grâce au 6 premier octets du CSS à trouvé: {s_attaque}.")
        else:
            print(f"Pour l'initialisation {s}, rien à été trouvé grâce à l'attaque.")
    input("")
    return demo()

demo()
