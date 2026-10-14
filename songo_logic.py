#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SONGO — jeu de mancala (Cameroun)
==================================
Programme console récrit en Python à partir des fiches « Règles du Songo ».

PLATEAU (A) : 2 camps de 7 cases, 5 pions par case.
BUT (B)     : capturer 40 pions.
COUP (C)    : on ramasse tous les pions d'une case de son camp et on les
              redistribue un par un dans les cases suivantes, dans le sens
              horaire (aiguilles d'une montre) :

                 Nord : n0 -> n1 -> ... -> n6 -> s6 -> s5 -> ... -> s0 -> n0

              On sème donc chez soi ET chez l'adversaire.

RÈGLES IMPLÉMENTÉES
-------------------
E  Grenier : plus de 13 pions dans la case jouée -> on fait un tour du
   plateau (13 cases, toutes sauf la case d'origine), puis on distribue
   les pions restants UNIQUEMENT dans le camp de l'adversaire.
F  Prise : le dernier pion semé tombe dans une case adverse qui contient
   alors 2, 3 ou 4 pions -> on la capture, et on continue vers les cases
   précédentes tant qu'elles contiennent 2, 3 ou 4 pions.
G  Interdits :
   1. on ne passe pas 1 pion chez l'adversaire avec la case la plus à
      gauche de son camp ; si c'est le seul coup possible, le pion est
      retiré du jeu et ajouté aux prises ;
   2. on ne passe pas 2 pions chez l'adversaire avec la case la plus à
      gauche, sauf si ce coup capture (l'interdit est alors annulé) ;
   3. on ne prive pas son adversaire de graines : s'il ne peut plus
      transmettre de pions, la partie s'arrête.
H  Solidarité :
   1. si l'adversaire n'a plus de pions, on DOIT jouer la première case
      à gauche de son camp (on lui transmet un maximum) ;
   2. on ne vide pas le camp adverse : un coup qui le viderait est joué
      mais ne rapporte AUCUNE prise.
I  Grenier : à la fin de la distribution d'un grenier, la prise s'applique
   normalement.
J  Fin : 40 pions capturés -> victoire ; moins de 10 pions en jeu ->
   chacun garde les pions de son camp ; impossible de transmettre -> fin.

NOTE : les exemples E (17 pions) et I (22 pions) imposent une seule
passe dans le camp adverse après le tour de 13 ; l'excédent y est retiré
du jeu. La prise annoncée dans l'exemple I (8 pions) est incohérente avec
son propre plateau dessiné : on applique la règle F telle qu'écrite.
Posez REGLE_E_GRENIERS = False pour un tour complet classique à la place.
"""

import copy
import random

TAILLE = 7                     # cases par camp
PIONS_DEPART = 5               # pions par case au départ
SEUIL_VICTOIRE = 40            # J : prises pour gagner
SEUIL_FIN = 10                 # J : fin si moins de 10 pions en jeu
REGLE_E_GRENIERS = True        # True : règle écrite E ; False : tour complet classique

NORD, SUD = "Nord", "Sud"


def lin(camp, i):
    """Index circulaire 0..13 de la case (camp, i), ordre n0..n6, s6..s0."""
    return i if camp == NORD else 2 * TAILLE - 1 - i


def camp_index(L):
    """Case (camp, i) correspondant à l'index circulaire L."""
    if L < TAILLE:
        return NORD, L
    return SUD, 2 * TAILLE - 1 - L


class Songo:
    """Une partie de Songo."""

    def __init__(self, premier=None):
        self.cases = {NORD: [PIONS_DEPART] * TAILLE,
                      SUD: [PIONS_DEPART] * TAILLE}
        self.prises = {NORD: 0, SUD: 0}
        self.joueur = premier if premier in (NORD, SUD) else random.choice([NORD, SUD])
        self.coups_joues = 0
        self.perdus = 0            # pions retirés du jeu (excédent d'un grenier)
        self.excedent = 0
        self.message = ""

    # ------------------------------------------------------------ utilitaires
    @staticmethod
    def autre(joueur):
        return SUD if joueur == NORD else NORD

    def total_camp(self, joueur):
        return sum(self.cases[joueur])

    def total_plateau(self):
        return self.total_camp(NORD) + self.total_camp(SUD)

    # ------------------------------------------------------------------ semis
    def _ajouter(self, L):
        camp, i = camp_index(L)
        self.cases[camp][i] += 1

    @staticmethod
    def _case_adverse_suivante(joueur, L):
        """Prochaine case du camp adverse après L (ordre circulaire)."""
        adv = Songo.autre(joueur)
        while True:
            L = (L + 1) % 14
            camp, _ = camp_index(L)
            if camp == adv:
                return L

    def _semer(self, joueur, idx, main):
        """Sème 'main' pions depuis la case idx (déjà vidée).
        Renvoie (indices semés, est_un_grenier)."""
        origine = lin(joueur, idx)
        L = origine
        semes = []
        grenier = main > 2 * TAILLE - 1
        if grenier and REGLE_E_GRENIERS:
            # E : un tour du plateau = 13 cases (toutes sauf l'origine)
            for _ in range(2 * TAILLE - 1):
                L = (L + 1) % 14
                if L == origine:
                    L = (L + 1) % 14
                self._ajouter(L)
                semes.append(L)
            main -= 2 * TAILLE - 1
            # puis UNE PASSE uniquement dans le camp adverse (7 cases, fiches E et I)
            L = self._case_adverse_suivante(joueur, L)
            for _ in range(TAILLE):
                if main <= 0:
                    break
                self._ajouter(L)
                semes.append(L)
                main -= 1
                L = self._case_adverse_suivante(joueur, L)
            if main > 0:          # excédent : retiré du jeu (exemple I de la fiche)
                self.perdus += main
                self.excedent = main
        else:
            while main > 0:
                L = (L + 1) % 14
                self._ajouter(L)
                semes.append(L)
                main -= 1
        return semes, grenier

    # ------------------------------------------------------------------ prises
    def resoudre_prises(self, joueur, semes, grenier):
        """Règle F (chaîne 2-3-4) + H2 (camp adverse non vidé).
        Renvoie le nombre de pions capturés."""
        adv = self.autre(joueur)
        total_adv = self.total_camp(adv)
        if total_adv == 0:
            return 0
        # case de départ de la chaîne de capture
        camp_d, _ = camp_index(semes[-1])
        depart = None
        if camp_d == adv:
            depart = semes[-1]                    # cas normal (règle F)
        elif grenier:                             # grenier : dernière case adverse semée
            for L in reversed(semes):
                camp, _ = camp_index(L)
                if camp == adv:
                    depart = L
                    break
        if depart is None:
            return 0
        # chaîne : en reculant tant que 2, 3 ou 4 pions
        chaine = []
        L = depart
        while True:
            camp, i = camp_index(L)
            if camp != adv or self.cases[camp][i] not in (2, 3, 4):
                break
            chaine.append(L)
            L = (L - 1) % 14
        if not chaine:
            return 0
        total = sum(self.cases[camp_index(x)[0]][camp_index(x)[1]] for x in chaine)
        if total_adv - total == 0:
            return 0                              # H2 : on ne vide pas le camp adverse
        for x in chaine:
            camp, i = camp_index(x)
            self.cases[camp][i] = 0
        return total

    # --------------------------------------------------------- coups autorisés
    def transmet(self, joueur, idx):
        """True si semer la case idx atteint le camp adverse."""
        main = self.cases[joueur][idx]
        if main <= 0:
            return False
        distance = (TAILLE - idx) if joueur == NORD else (idx + 1) % 14
        return main >= distance

    def capture_attendue(self, joueur, idx):
        """Nombre de pions que rapporterait le coup (simulation)."""
        g = copy.deepcopy(self)
        avant = g.prises[joueur]
        g.jouer_coup(joueur, idx)
        return g.prises[joueur] - avant

    def coups_legaux(self, joueur):
        camp = self.cases[joueur]
        adv = self.autre(joueur)
        non_vides = [i for i in range(TAILLE) if camp[i] > 0]
        if not non_vides:
            return []
        # H1 : adversaire sans pions -> obligation de transmettre
        if self.total_camp(adv) == 0:
            transmetteurs = [i for i in non_vides if self.transmet(joueur, i)]
            return transmetteurs[:1]              # la plus à gauche
        legaux = []
        for i in non_vides:
            if i == 0:                            # case la plus à gauche
                if camp[i] == 1:
                    continue                      # G1
                if camp[i] == 2 and self.capture_attendue(joueur, i) == 0:
                    continue                      # G2 (annulé si capture)
            legaux.append(i)
        if not legaux:
            # G1, seul coup possible : le pion sera retiré du jeu
            if non_vides == [0] and camp[0] == 1:
                return [0]
            return non_vides                      # secours (ne devrait pas arriver)
        return legaux

    # ------------------------------------------------------------- jeu d'un coup
    def jouer_coup(self, joueur, idx):
        camp = self.cases[joueur]
        main = camp[idx]
        # G1, seul coup possible : 1 pion sur la case la plus à gauche
        if idx == 0 and main == 1 and all(camp[i] == 0 for i in range(1, TAILLE)):
            camp[idx] = 0
            self.prises[joueur] += 1
            self.message = (f"{joueur} : seul coup possible, le pion de la case 1 "
                            f"est retiré du jeu (G1) et ajouté à ses prises.")
        else:
            camp[idx] = 0
            self.excedent = 0
            semes, grenier = self._semer(joueur, idx, main)
            prises = self.resoudre_prises(joueur, semes, grenier)
            self.prises[joueur] += prises
            if self.excedent:
                self.message = (f"{main} pions dans ce grenier : {self.excedent} "
                                f"pion(s) au-delà de la passe adverse retiré(s) du jeu.")
            if prises:
                self.message = f"{joueur} capture {prises} pion(s) !"
            elif grenier:
                self.message = f"{joueur} a distribué un grenier ({main} pions), aucune prise."
            else:
                self.message = ""
        self.joueur = self.autre(joueur)
        self.coups_joues += 1

    # ---------------------------------------------------------------- fin partie
    def partie_finie(self):
        if self.prises[NORD] >= SEUIL_VICTOIRE or self.prises[SUD] >= SEUIL_VICTOIRE:
            return True
        if self.total_plateau() < SEUIL_FIN:
            return True
        if not self.coups_legaux(self.joueur):
            return True                           # plus de pions ou transmission impossible
        return False


# ==================================================================== affichage
def afficher(g):
    n, s = g.cases[NORD], g.cases[SUD]
    barre = lambda a, b, c: a + b.join(["────"] * TAILLE) + c
    print()
    print(f"  Prises -> Nord : {g.prises[NORD]:>2}   |   Sud : {g.prises[SUD]:>2}"
          f"   (victoire : {SEUIL_VICTOIRE} pions)")
    print("        " + barre("┌", "┬", "┐"))
    print("  Nord  │" + "│".join(f" {v:>2} " for v in n) + "│")
    print("        " + barre("├", "┴", "┤"))
    print("  Sud   │" + "│".join(f" {v:>2} " for v in s) + "│")
    print("        " + barre("└", "┴", "┘"))
    print("          " + "   ".join(f" {i + 1}  " for i in range(TAILLE)))
    print(f"  >> Au tour de : {g.joueur}")


def annoncer_resultat(g):
    print()
    if g.prises[NORD] >= SEUIL_VICTOIRE:
        raison = f"{NORD} a atteint {SEUIL_VICTOIRE} prises"
    elif g.prises[SUD] >= SEUIL_VICTOIRE:
        raison = f"{SUD} a atteint {SEUIL_VICTOIRE} prises"
    elif g.total_plateau() < SEUIL_FIN:
        raison = "moins de 10 pions restent en jeu"
    else:
        raison = "un joueur ne peut plus transmettre de pions"
    print(f"Partie terminée ({raison}).")
    for j in (NORD, SUD):
        g.prises[j] += g.total_camp(j)            # chacun garde les pions de son camp
    print(f"  Total -> Nord : {g.prises[NORD]} pions   |   Sud : {g.prises[SUD]} pions")
    if g.prises[NORD] > g.prises[SUD]:
        print(f"  >>> {NORD} gagne !")
    elif g.prises[SUD] > g.prises[NORD]:
        print(f"  >>> {SUD} gagne !")
    else:
        print("  >>> Égalité !")


# ========================================================================== IA
def coup_ia(g, joueur):
    """IA gloutonne : maximise (prises immédiates - meilleure réplique adverse)."""
    legaux = g.coups_legaux(joueur)
    adv = g.autre(joueur)
    meilleur, meilleur_score = None, None
    for idx in legaux:
        g1 = copy.deepcopy(g)
        avant = g1.prises[joueur]
        g1.jouer_coup(joueur, idx)
        gain = g1.prises[joueur] - avant
        replique = 0
        for j2 in g1.coups_legaux(adv):
            g2 = copy.deepcopy(g1)
            avant2 = g2.prises[adv]
            g2.jouer_coup(adv, j2)
            replique = max(replique, g2.prises[adv] - avant2)
        score = (gain - replique) + random.random() * 0.01
        if meilleur_score is None or score > meilleur_score:
            meilleur, meilleur_score = idx, score
    return meilleur


# ======================================================================== main
def main():
    print("=" * 56)
    print("                 S O N G O")
    print("      2 camps x 7 cases - 5 pions par case")
    print("=" * 56)
    mode = input("Mode : (1) deux joueurs   (2) contre l'ordinateur [1] : ").strip() or "1"
    ia = None
    if mode == "2":
        camp = input("Tu joues (N)ord ou (S)ud ? [N] : ").strip().upper() or "N"
        ia = SUD if camp.startswith("N") else NORD
    g = Songo()
    print(f"\n{g.joueur} commence.")
    while not g.partie_finie():
        afficher(g)
        j = g.joueur
        legaux = g.coups_legaux(j)
        if ia == j:
            idx = coup_ia(g, j)
            print(f"{j} (ordinateur) joue la case {idx + 1}.")
        else:
            while True:
                saisie = input(f"{j}, choisis une case {sorted(i + 1 for i in legaux)}"
                               f" ('q' pour quitter) : ").strip().lower()
                if saisie in ("q", "quitter"):
                    print("Partie interrompue.")
                    return
                if saisie.isdigit() and int(saisie) - 1 in legaux:
                    idx = int(saisie) - 1
                    break
                print("  -> coup invalide, réessaie.")
        g.jouer_coup(j, idx)
        if g.message:
            print(f"  -> {g.message}")
    afficher(g)
    annoncer_resultat(g)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPartie interrompue.")
