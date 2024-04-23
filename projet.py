import random

# classe pour creer un lfsr
class LFSR:
    # prend en entrée une liste de 0 et de 1 et la position des bits non-nuls du coefficients de retroaction
    def __init__(self, s:list, c_non_nuls:list=[0]):
        self.s = s
        c = [0] * (len(s))
        for elem in c_non_nuls:
            c[(len(s)-1)-elem] = 1
        self.c = c
        self.s_default = s

    # décale les bits et génère un bit de remplacement grace aux coefficients de retroaction
    # retourne le premier bit
    def decalage(self):
        b = 0
        for i in range(len(self.s)):
            b = (b + self.c[i] * self.s[i]) % 2
        s0 = self.s[-1]
        self.s = [b] + self.s[:-1]
        return s0

    # fais 8 décalages et renvoie les 8 bits renvoyé
    def generer_octet(self):
        octet = []
        for _ in range(8):
            octet = [self.decalage()] + octet
        return octet
    
    # reinitialise la clé
    def remise_par_default(self):
        self.s = self.s_default

    # methode de verification
    # pour savoir si il y a bien 2**(taille du lfsr) configuration
    def verif_random(self):
        # on prend la taille du lfsr
        size = len(self.s)
        # on fais une boucle pour generer un s
        while True:
            # liste pour generer un s aleatoire
            s_random = []
            # chaine de caractère pour pouvoir mettre tout les chiffres généré
            str_s = ""
            # genere s avec des 0 ou des 1 aleatoirement de la taille du lfsr
            for i in range(size):
                s_random.append(random.randint(0, 1))
            # mets tout les chiffres dans la chaine de caractère
            for elem in s_random:
                str_s += str(elem)
            # si la on a pas genere que des 0 on sort de la boucle sinon on recommence
            if str_s != "0"*size:
                break
        # on garde l'ancien s du lfsr pour pouvoir le remettre après
        ancien_s = self.s
        # on mets le s genere aleatoirement dans le lfsr
        self.s = s_random
        # creer un set pour pouvoir mettre toutes les configurations du lfsr dedans
        config = set()
        # on fais tourner le lfsr 2**(taille du lfsr)-1 qui est le nombre max de configuration possible
        for i in range((2**size-1)):
            print(f"Configuration numéro : {i+1}, {self.s}")
            # on ajoute la configuration actuel dans le set
            config.add(str(self.s))
            # on fais tourner le lfsr le nombre de fois qu'il faut pour qu'une nouvelle serie soit a l'intérieur
            for j in range(size):
                self.decalage()
            # et on recommence
        # on regarde si le set contient bien 2**(taille du lfsr)-1 élément
        # car un set ne peut pas contenir 2 éléments identique donc si 2 configurations sont identique
        # il en manquera un dans le set
        if len(config) == (2**size)-1:
            # on remet la configuration du lfsr qu'il y avait avant la vérification
            self.s = ancien_s
            # on retourne vrai
            return True
        # si il manque au moins un élément on retourne faux
        else:
            # on remet la configuration du lfsr qu'il y avait avant la vérification
            self.s = ancien_s
            # on retourne faux
            return False

# classe pour creer un css
class CSS:
    # il prend en entrée que la clé secrète de 40 bits
    # et créer grâce a cela les 2 lsfr qui le compose
    def __init__(self, s:list):
        self.lsfr17 = LFSR([1]+s[:16], [14, 0])
        self.lsfr25 = LFSR([1]+s[16:], [12, 4, 3, 0])
        self.c = 0

    # grace aux 2 lsfr créé et a la methode de classe genrer_octet
    # transforme juste les octets reçu en décimal fais le calcul
    # fais le test pour le c et renvoie z sous forme de liste binaire
    def genere_cle(self):
        x = int(''.join(str(elem) for elem in self.lsfr17.generer_octet()), 2)
        y = int(''.join(str(elem) for elem in self.lsfr25.generer_octet()), 2)
        z = (x + y + self.c) % 256
        self.c = 1 if x + y > 255 else 0
        # transforme le z qui est un entier en binaire sous forme de liste
        k = [int(elem) for elem in str(bin(z))[2:]]
        # rajoute des 0 devant pour completer jusqu'à 8 bits
        while len(k) < 8:
            k = [0] + k
        return k
  
    # methode pour chiffer et dechiffrer le message
    def chiffrer_dechiffrer(self, m:list):
        # remet la suite binaire du lfsr à 0
        self.lsfr17.remise_par_default()
        self.lsfr25.remise_par_default()
        c = []
        # chiffre ou dechiffre le message d'octet en octet
        while len(m)>0:
            cle = self.genere_cle()
            for elem, k in zip(m[:8], cle):
                c.append((elem+k)%2)
            m = m[8:]
        return c

# fonction pour générer un s et 6 z pour le test de l'attaque
def generer_z():
    # creer une liste pour contenir la configuration du css
    s = []
    # creer 40 0 ou 1 aléatoirement
    for i in range(40):
        s.append(random.randint(0,1))
    # ligne de test
    # s = [1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0]
    # creer un css avec le s aleatoire
    css = CSS(s)
    # creation d'une liste pour les 6 premier z
    z = []
    # on fais tourner le css 6 fois pour avoir les 6 premier clé
    for i in range(6):
        z.append(css.genere_cle())
    # on retourne le s utilisé pour pouvoir comparer la réponse de l'attaque
    # avec la liste de z pour l'attaque
    return s, z

# fonction d'attaque d'un css
# il prend en entrée les 6 premiers z d'un css
def attaque_css(z:list):
    # il va tester les 2**16 possibilité pour l'initialisation du lfsr17
    for i in range(2**16):
        # créer une nouvelle liste avec les éléments qui sont sous forme de liste dans z
        # en entier base 10
        z_int = []
        for liste in z:
            z_int.append(int(int(''.join(str(elem) for elem in liste), 2)))
        # création de l'initialisation x pour le lfsr17
        random_x = [1]
        # pour le resultat du lfsr17
        x = []
        # resultat sous forme entier base 10 du lsfr17
        x_int = []
        # pour le resultat du calcule de y grace a x et z
        y = []
        # resutlat sous forme d'entier
        y_int = []
        # pour initialiser les css de test pour savoir si les 6 premier z sont correcte
        s = []
        # on prend les i dans l'ordre pour trouver le x correspondant au lsfr17 du css
        # on le mets en base 2 dans une liste car le lfsr prend une liste en entrée
        for elem in str(format(i, '016b')):
            random_x.append(int(elem))
        # création du lfsr17
        lfsr = LFSR(random_x, [14, 0])
        # sortie des 3 premiers x
        for j in range(3):
            x = [lfsr.generer_octet()] + x
            x_int = [int(int(''.join(str(elem) for elem in x[0]), 2))] + x_int
        # calcule du y, c = 1 quand le z-x d'avant < 0, 0 sinon
        c = 0
        for j in range(3):
            y_int.append((z_int[j] - x_int[2-j] - c) % 256)
            # met c a 1 si z-x < 0 sinon met un 0
            c = 1 if z_int[j] - x_int[2-j] < 0 else 0
            # ajoute dans la liste y sous forme liste binaire pour pouvoir initialisé le css
            y.append([])
            y = [[]] + y
            for elem in str(format(y_int[j], '08b')):
                y[0].append(int(elem))
        # création du s avec les 40 bits d'initialisation
        # 2 premier octets de x
        for j in range(1, 3):
            s += x[j]
        # 3 octets de y calculer precedement
        for elem in y:
            s += elem
        # création du css de test
        css = CSS(s)
        z_prime = []
        # génération des 6 z
        for j in range(6):
            z_prime.append(css.genere_cle())
        # verification des z
        # si les z générer sont les mêmes que les 6 connues alors on arrete la boucle et on renvoie le resultat
        if z_prime == z:
            return s
    # retourne faux si rien trouvé
    return False

# test de l'attaque
s, z = generer_z()
# s généré aleatoirement
print(f"s généré aléatoirement:\n{s}")
# s obtenu grace a l'attaque
print(f"s trouvé grâce à l'attaque:\n{attaque_css(z)}")

# test du css
"""
m = []
for elem in str(bin(0xffffffffff))[2:]:
    m.append(int(elem))
s = [0] * 40
css = CSS(s)
print("0xffffffffff")
c = css.chiffrer_dechiffrer(m)
d = css.chiffrer_dechiffrer(c)
c = hex(int(''.join(str(elem) for elem in c), 2))
d = hex(int(''.join(str(elem) for elem in d), 2))

print(c)
print(d)
"""
