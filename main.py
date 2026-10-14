# -*- coding: utf-8 -*-
"""Interface tactile Android pour le jeu SONGO. Dépendance : Kivy."""
import random
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.clock import Clock

from songo_logic import Songo, NORD, SUD, SEUIL_VICTOIRE, SEUIL_FIN, coup_ia

class SongoAndroid(App):
    def build(self):
        self.title = "SONGO"
        self.root_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        self.root_box.add_widget(Label(text="[b]S O N G O[/b]\\nJeu traditionnel camerounais",
                                       markup=True, size_hint_y=None, height=dp(58), font_size="22sp"))
        options = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        self.mode = Spinner(text="Deux joueurs", values=("Deux joueurs", "Contre l'ordinateur"),
                            size_hint_x=0.65)
        self.human = Spinner(text="Je joue Nord", values=("Je joue Nord", "Je joue Sud"),
                             size_hint_x=0.65)
        options.add_widget(self.mode)
        options.add_widget(self.human)
        self.root_box.add_widget(options)
        self.status = Label(text="", size_hint_y=None, height=dp(48), halign="center",
                            valign="middle", font_size="16sp")
        self.status.bind(size=lambda obj, val: setattr(obj, "text_size", val))
        self.root_box.add_widget(self.status)
        self.board = GridLayout(cols=7, spacing=dp(5), size_hint_y=None, height=dp(180))
        self.root_box.add_widget(self.board)
        self.note = Label(text="", size_hint_y=None, height=dp(45), font_size="13sp",
                          halign="center", valign="middle")
        self.note.bind(size=lambda obj, val: setattr(obj, "text_size", val))
        self.root_box.add_widget(self.note)
        controls = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        controls.add_widget(Button(text="Nouvelle partie", on_release=lambda *_: self.new_game()))
        controls.add_widget(Button(text="Règles", on_release=lambda *_: self.show_rules()))
        self.root_box.add_widget(controls)
        self.new_game()
        return self.root_box

    def new_game(self):
        self.ai_side = None
        if self.mode.text == "Contre l’ordinateur" or self.mode.text == "Contre l'ordinateur":
            self.ai_side = SUD if self.human.text == "Je joue Nord" else NORD
        self.game = Songo()
        self.note.text = "Touchez une case de votre camp pour jouer."
        self.refresh()
        Clock.schedule_once(lambda dt: self.maybe_ai(), 0.2)

    def refresh(self):
        self.board.clear_widgets()
        # Nord de gauche à droite, Sud de droite à gauche pour visualiser le parcours circulaire.
        for i, value in enumerate(self.game.cases[NORD]):
            b = Button(text=f"{value}", font_size="22sp", bold=True,
                       background_normal="", background_color=(0.20, 0.48, 0.32, 1),
                       color=(1,1,1,1))
            b.bind(on_release=lambda btn, idx=i: self.play(NORD, idx))
            self.board.add_widget(b)
        for visual_i in range(6, -1, -1):
            value = self.game.cases[SUD][visual_i]
            b = Button(text=f"{value}", font_size="22sp", bold=True,
                       background_normal="", background_color=(0.62, 0.38, 0.17, 1),
                       color=(1,1,1,1))
            b.bind(on_release=lambda btn, idx=visual_i: self.play(SUD, idx))
            self.board.add_widget(b)
        self.status.text = (f"Tour : {self.game.joueur}     |     "
                            f"Prises Nord : {self.game.prises[NORD]}   •   "
                            f"Sud : {self.game.prises[SUD]}")
        self.note.text = self.game.message or "Nord en haut • Sud en bas — choisissez une case de votre camp."
        if self.game.partie_finie():
            Clock.schedule_once(lambda dt: self.finish_popup(), 0.1)

    def play(self, side, idx):
        if self.game.partie_finie():
            return
        if side != self.game.joueur:
            self.note.text = f"Ce n'est pas le camp {side} qui doit jouer."
            return
        if self.ai_side == side:
            return
        legal = self.game.coups_legaux(side)
        if idx not in legal:
            self.note.text = "Coup interdit ou case vide. Cases jouables : " + ", ".join(str(i+1) for i in legal)
            return
        self.game.jouer_coup(side, idx)
        self.refresh()
        Clock.schedule_once(lambda dt: self.maybe_ai(), 0.25)

    def maybe_ai(self):
        if self.ai_side and self.game.joueur == self.ai_side and not self.game.partie_finie():
            move = coup_ia(self.game, self.ai_side)
            if move is not None:
                self.game.jouer_coup(self.ai_side, move)
                self.refresh()

    def finish_popup(self):
        if getattr(self, "_showing_end", False):
            return
        self._showing_end = True
        totals = {side: self.game.prises[side] + self.game.total_camp(side) for side in (NORD, SUD)}
        if totals[NORD] > totals[SUD]:
            winner = "Nord gagne !"
        elif totals[SUD] > totals[NORD]:
            winner = "Sud gagne !"
        else:
            winner = "Égalité !"
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        content.add_widget(Label(text=f"Partie terminée\\nNord : {totals[NORD]} — Sud : {totals[SUD]}\\n{winner}"))
        btn = Button(text="Fermer", size_hint_y=None, height=dp(44))
        content.add_widget(btn)
        pop = Popup(title="Résultat", content=content, size_hint=(0.85, 0.4), auto_dismiss=False)
        btn.bind(on_release=pop.dismiss)
        pop.bind(on_dismiss=lambda *_: setattr(self, "_showing_end", False))
        pop.open()

    def show_rules(self):
        text = ("But : atteindre 40 prises. Chaque joueur choisit une case de son camp "
                "et sème les pions un par un dans le sens horaire. Les captures et coups "
                "interdits suivent les règles intégrées au programme d'origine. "
                "La partie se termine aussi lorsqu'il reste moins de 10 pions ou qu'aucun "
                "coup de transmission n'est possible.")
        Popup(title="Règles du Songo", content=Label(text=text, padding=dp(12)),
              size_hint=(0.9, 0.5)).open()

if __name__ == "__main__":
    SongoAndroid().run()
