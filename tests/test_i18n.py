"""
Tests unitaires pour le module d'internationalisation i18n.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multipli.i18n import I18n, _


class TestI18n(unittest.TestCase):
    def setUp(self):
        self.i18n = I18n.get_instance()
        self.i18n.set_language("fr")

    def test_available_languages(self):
        langs = self.i18n.get_available_languages()
        codes = [c for c, _, _ in langs]
        self.assertIn("fr", codes)
        self.assertIn("en", codes)
        self.assertIn("es", codes)
        self.assertIn("de", codes)

    def test_translations_fr(self):
        self.i18n.set_language("fr")
        self.assertEqual(_("app_title"), "Multipli")
        self.assertEqual(_("nav_adventure"), "Aventure")
        self.assertIn("CE1", _("mode_ce1_title"))

    def test_translations_en(self):
        self.i18n.set_language("en")
        self.assertEqual(_("nav_adventure"), "Adventure")
        self.assertEqual(_("btn_start"), "Start")

    def test_translations_es(self):
        self.i18n.set_language("es")
        self.assertEqual(_("nav_adventure"), "Aventura")
        self.assertEqual(_("btn_start"), "Empezar")

    def test_translations_de(self):
        self.i18n.set_language("de")
        self.assertEqual(_("nav_adventure"), "Abenteuer")
        self.assertEqual(_("btn_start"), "Starten")

    def test_variable_interpolation(self):
        self.i18n.set_language("fr")
        text = _("question_progress", current=3, total=10)
        self.assertIn("3", text)
        self.assertIn("10", text)

    def test_fallback_on_missing_key(self):
        self.i18n.set_language("es")
        # Clé inexistante retourne la clé elle-même
        self.assertEqual(_("non_existent_key_xyz"), "non_existent_key_xyz")

    def test_language_change_listener(self):
        notified = []
        def listener(code):
            notified.append(code)

        self.i18n.add_listener(listener)
        self.i18n.set_language("en")
        self.assertIn("en", notified)
        self.i18n.remove_listener(listener)


if __name__ == "__main__":
    unittest.main()
