"""
Tests d'intégration complets pour le moteur de jeu, le replay et les modes de saisie.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
Adw.init()

from multipli.game_view import GameView
from multipli.adventure_view import AdventureView
from multipli.dojo_view import DojoView
from multipli.time_attack_view import TimeAttackView
from multipli.models import StorageManager


class TestGameLoop(unittest.TestCase):
    def setUp(self):
        self.back_called = False
        def on_back():
            self.back_called = True
        self.gv = GameView(on_back)

    def test_qcm_complete_game_and_replay(self):
        """Vérifie le cycle complet d'une partie QCM et le bon affichage des choix au Rejouer."""
        # 1. Démarrer une partie QCM de 3 questions
        self.gv.start_game(tables=[3], total_questions=3, input_mode="qcm")

        self.assertTrue(self.gv.input_stack.get_visible())
        self.assertEqual(self.gv.input_stack.get_visible_child_name(), "qcm")
        self.assertTrue(self.gv.qcm_box.get_visible())
        self.assertEqual(len(self.gv.questions), 3)

        # 2. Répondre aux 3 questions
        for idx in range(3):
            self.assertEqual(self.gv.current_idx, idx)
            q = self.gv.questions[idx]
            correct = q.correct_answer
            opts = self.gv.qcm_options
            self.assertIn(correct, opts)
            btn_idx = opts.index(correct)

            # Clic sur le bon bouton
            self.gv._on_qcm_button_clicked(btn_idx)
            self.assertEqual(self.gv.score, idx + 1)
            self.assertEqual(self.gv.streak, idx + 1)

            # Passage à la question suivante
            self.gv._next_question()

        # 3. Écran de fin affiché
        self.assertEqual(self.gv.current_idx, 3)
        self.assertTrue(self.gv.results_btn_box.get_visible())
        self.assertFalse(self.gv.input_stack.get_visible())

        # 4. TEST CRITIQUE : Rejouer
        self.gv._on_retry_clicked(None)

        # Vérifier que l'état est réinitialisé et que les choix QCM sont réaffichés
        self.assertEqual(self.gv.current_idx, 0)
        self.assertEqual(self.gv.score, 0)
        self.assertEqual(self.gv.streak, 0)
        self.assertFalse(self.gv.results_btn_box.get_visible())
        self.assertTrue(self.gv.input_stack.get_visible(), "L'input_stack doit être visible après Rejouer")
        self.assertEqual(self.gv.input_stack.get_visible_child_name(), "qcm")
        self.assertTrue(self.gv.qcm_box.get_visible(), "La boîte QCM doit être visible après Rejouer")

        # Vérifier que les 4 boutons ont de nouvelles options non vides et cliquables
        self.assertEqual(len(self.gv.qcm_options), 4)
        for b in self.gv.qcm_buttons:
            self.assertTrue(b.get_sensitive())
            self.assertTrue(len(b.get_label()) > 0)

        # Répondre à nouveau sur la partie rejouée
        q_replay = self.gv.questions[0]
        correct_idx = self.gv.qcm_options.index(q_replay.correct_answer)
        self.gv._on_qcm_button_clicked(correct_idx)
        self.assertEqual(self.gv.score, 1)

    def test_keypad_mode(self):
        """Vérifie le fonctionnement du mode pavé numérique."""
        self.gv.start_game(tables=[5], total_questions=2, input_mode="keypad")

        self.assertTrue(self.gv.input_stack.get_visible())
        self.assertEqual(self.gv.input_stack.get_visible_child_name(), "keypad")
        self.assertTrue(self.gv.input_display_box.get_visible())

        # Saisie d'un nombre (ex: "15")
        self.gv._append_digit("1")
        self.gv._append_digit("5")
        self.assertEqual(self.gv.user_input_buffer, "15")
        self.assertEqual(self.gv.input_display_label.get_label(), "15")

        # Effacer
        self.gv._clear_input()
        self.assertEqual(self.gv.user_input_buffer, "")

        # Saisir la bonne réponse
        q = self.gv.questions[0]
        for digit in str(q.correct_answer):
            self.gv._append_digit(digit)

        self.gv._submit_keypad_answer()
        self.assertEqual(self.gv.score, 1)

    def test_keypad_enter_key_validation(self):
        """Vérifie que les touches Entrée (Return et KP_Enter) valident la saisie du pavé."""
        from gi.repository import Gdk

        self.gv.start_game(tables=[4], total_questions=3, input_mode="keypad")
        q0 = self.gv.questions[0]

        # 1. Taper la bonne réponse avec les touches du pavé numérique physique (Gdk.KEY_KP_X)
        for d in str(q0.correct_answer):
            kp_key = getattr(Gdk, f"KEY_KP_{d}")
            handled = self.gv.handle_key(kp_key)
            self.assertTrue(handled)

        self.assertEqual(self.gv.user_input_buffer, str(q0.correct_answer))

        # 2. Appuyer sur Entrée du pavé numérique (Gdk.KEY_KP_Enter)
        handled = self.gv.handle_key(Gdk.KEY_KP_Enter)
        self.assertTrue(handled, "Gdk.KEY_KP_Enter doit être intercepté et validé")
        self.assertTrue(self.gv.is_answered, "La question doit être marquée comme répondue")
        self.assertEqual(self.gv.score, 1, "Le score doit être incrémenté avec la touche Entrée KP")

        # 3. Passer à la question suivante avec Entrée
        self.gv.handle_key(Gdk.KEY_KP_Enter)
        self.assertEqual(self.gv.current_idx, 1)

        # 4. Taper la réponse à la question 1 et valider avec Entrée clavier classique (Gdk.KEY_Return)
        q1 = self.gv.questions[1]
        for d in str(q1.correct_answer):
            self.gv.handle_key(getattr(Gdk, f"KEY_{d}"))

        handled = self.gv.handle_key(Gdk.KEY_Return)
        self.assertTrue(handled, "Gdk.KEY_Return doit valider la réponse")
        self.assertTrue(self.gv.is_answered)
        self.assertEqual(self.gv.score, 2)

    def test_adventure_view_unlock_logic(self):
        """Vérifie le déblocage des niveaux selon la classe et les étoiles."""
        storage = StorageManager.get_instance()
        p = storage.get_active_profile()

        # Profil en CE1
        p.start_level = "ce1"
        p.stars = {"ce1": 0, "ce2": 0, "cm1": 0, "cm2": 0}
        adv = AdventureView(lambda cfg: None)

        # Obtenir les cartes
        cards = []
        child = adv.levels_container.get_first_child()
        while child:
            cards.append(child)
            child = child.get_next_sibling()

        self.assertEqual(len(cards), 4)

        # En passant en CM1, CE1/CE2/CM1 sont débloqués
        p.start_level = "cm1"
        adv.refresh_levels()
        # Vérifié sans crash

    def test_dojo_view_configuration(self):
        """Vérifie la configuration personnalisée du Dojo libre."""
        started_config = []
        dojo = DojoView(lambda cfg: started_config.append(cfg))

        # Activer les tables 6 et 7
        for i, b in enumerate(dojo.table_buttons):
            b.set_active((i + 1) in [6, 7])

        dojo.radio_qcm.set_active(True)
        dojo.btn_q15.set_active(True)
        dojo.radio_mixed.set_active(True)

        dojo._on_start_clicked(None)

        self.assertEqual(len(started_config), 1)
        cfg = started_config[0]
        self.assertEqual(cfg["tables"], [6, 7])
        self.assertEqual(cfg["total_questions"], 15)
        self.assertEqual(cfg["input_mode"], "qcm")
        self.assertEqual(cfg["question_types"], ["direct", "missing_factor_a", "missing_factor_b"])

    def test_time_attack_view(self):
        """Vérifie le mode contre-la-montre 60s."""
        t_view = TimeAttackView(lambda: None)
        self.assertEqual(t_view.stack.get_visible_child_name(), "intro")

        # Lancer le chrono
        t_view._on_start_chrono(None)
        self.assertEqual(t_view.stack.get_visible_child_name(), "playing")
        self.assertIsNotNone(t_view.current_question)

        # Répondre correctement
        initial_score = t_view.score
        t_view._check_answer(t_view.current_question.correct_answer)
        self.assertEqual(t_view.score, initial_score + 1)

        # Fin du chrono
        t_view._end_chrono()
        self.assertEqual(t_view.stack.get_visible_child_name(), "results")


if __name__ == "__main__":
    unittest.main()
