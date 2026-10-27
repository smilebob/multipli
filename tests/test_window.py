"""
Tests d'intégration de bout en bout pour la fenêtre principale et la navigation.
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

from main import MultipliApplication
from multipli.window import MultipliWindow
from multipli.profiles_dialog import ProfilesDialog, EditProfileDialog
from multipli.preferences_dialog import PreferencesDialog
from multipli.models import StorageManager


class TestWindowE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = MultipliApplication()
        cls.app.register(None)
        cls.app.do_startup()
        cls.win = MultipliWindow(application=cls.app)

    def test_window_initialized_and_views_accessible(self):
        self.assertIsNotNone(self.win.toolbar_view.get_content())
        self.assertEqual(self.win.view_stack.get_visible_child_name(), "adventure")

        # Basculer sur le Dojo
        self.win.view_stack.set_visible_child_name("dojo")
        self.assertEqual(self.win.view_stack.get_visible_child_name(), "dojo")

        # Basculer sur Chrono
        self.win.view_stack.set_visible_child_name("chrono")
        self.assertEqual(self.win.view_stack.get_visible_child_name(), "chrono")

        # Basculer sur Pythagore
        self.win.view_stack.set_visible_child_name("pythagore")
        self.assertEqual(self.win.view_stack.get_visible_child_name(), "pythagore")

        # Basculer sur Stats
        self.win.view_stack.set_visible_child_name("stats")
        self.assertEqual(self.win.view_stack.get_visible_child_name(), "stats")

    def test_adventure_to_game_and_back(self):
        lvl = {
            "id": "ce1",
            "title": "Niveau CE1",
            "desc": "",
            "badge": "🌱",
            "tables": [2, 5],
            "input_mode": "qcm",
            "types": ["direct"],
            "count": 2,
            "unlocked": True,
        }
        self.win._start_adventure_level(lvl)
        self.assertEqual(self.win.view_stack.get_visible_child_name(), "game")
        self.assertTrue(self.win.game_view.input_stack.get_visible())

        # Retour à l'aventure
        self.win._on_game_back()
        self.assertEqual(self.win.view_stack.get_visible_child_name(), "adventure")

    def test_window_routes_enter_key_to_game(self):
        from gi.repository import Gdk

        cfg = {
            "tables": [5],
            "total_questions": 2,
            "input_mode": "keypad",
            "question_types": ["direct"],
            "level_id": None,
        }
        self.win._start_dojo_game(cfg)
        self.assertEqual(self.win.view_stack.get_visible_child_name(), "game")

        # Simuler la frappe au niveau de la fenêtre avec Gdk.KEY_KP_Enter
        q = self.win.game_view.questions[0]
        for d in str(q.correct_answer):
            self.win._on_window_key_pressed(None, getattr(Gdk, f"KEY_KP_{d}"), 0, 0)

        # Valider avec Entrée du pavé numérique au niveau de la fenêtre
        res = self.win._on_window_key_pressed(None, Gdk.KEY_KP_Enter, 0, 0)
        self.assertTrue(res)
        self.assertTrue(self.win.game_view.is_answered)
        self.assertEqual(self.win.game_view.score, 1)

        self.win._on_game_back()

    def test_dojo_to_game_and_back(self):
        cfg = {
            "tables": [3, 4],
            "total_questions": 2,
            "input_mode": "keypad",
            "question_types": ["direct"],
            "level_id": None,
        }
        self.win._start_dojo_game(cfg)
        self.assertEqual(self.win.view_stack.get_visible_child_name(), "game")
        self.assertTrue(self.win.game_view.input_stack.get_visible())
        self.assertEqual(self.win.game_view.input_stack.get_visible_child_name(), "keypad")

        self.win._on_game_back()
        self.assertEqual(self.win.view_stack.get_visible_child_name(), "adventure")

    def test_window_routes_enter_key_to_game(self):
        from gi.repository import Gdk

        cfg = {
            "tables": [5],
            "total_questions": 2,
            "input_mode": "keypad",
            "question_types": ["direct"],
            "level_id": None,
        }
        self.win._start_dojo_game(cfg)
        self.assertEqual(self.win.view_stack.get_visible_child_name(), "game")

        # Simuler la frappe au niveau de la fenêtre avec Gdk.KEY_KP_Enter
        q = self.win.game_view.questions[0]
        for d in str(q.correct_answer):
            self.win._on_window_key_pressed(None, getattr(Gdk, f"KEY_KP_{d}"), 0, 0)

        # Valider avec Entrée du pavé numérique au niveau de la fenêtre
        res = self.win._on_window_key_pressed(None, Gdk.KEY_KP_Enter, 0, 0)
        self.assertTrue(res)
        self.assertTrue(self.win.game_view.is_answered)
        self.assertEqual(self.win.game_view.score, 1)

        self.win._on_game_back()

    def test_dialogs_instantiation(self):
        p = StorageManager.get_instance().get_active_profile()
        dlg_prof = ProfilesDialog(self.win, lambda: None)
        self.assertIsNotNone(dlg_prof)

        dlg_edit = EditProfileDialog(self.win, p, lambda: None)
        self.assertIsNotNone(dlg_edit)

        dlg_pref = PreferencesDialog(self.win)
        self.assertIsNotNone(dlg_pref)


if __name__ == "__main__":
    unittest.main()
