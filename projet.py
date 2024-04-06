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
    
    def remise_par_default(self):
        self.s = self.s_default

# classe pour creer un css
class CSS:
    # il prend en entrée que la clé secrète de 40 bits
    # et créer grâce a cela les 2 lsfr qui le compose
    def __init__(self, s:list):
        self.lsfr17 = LFSR([1]+s[:16], [14, 0])
        self.lsfr25 = LFSR([1]+s[16:], [12, 4, 3, 0])
        self.c = 0

    # grace au 2 lsfr créé et a la fonction de classe genrer_octet
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
  
    # fonction pour chiffer et dechiffrer le message
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

m = []
for elem in str(bin(0xffffffffff))[2:]:
    m.append(int(elem))
s = [0] * 40
css = CSS(s)
c = css.chiffrer_dechiffrer(m)
d = css.chiffrer_dechiffrer(c)
c = hex(int(''.join(str(elem) for elem in c), 2))
d = hex(int(''.join(str(elem) for elem in d), 2))
