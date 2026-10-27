#!/usr/bin/env python3
"""
Multipli - Point d'entrée de l'application native GNOME.
"""

import sys
import os

# S'assurer que le module multipli est trouvable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib

from multipli import __version__, __app_id__
from multipli.i18n import I18n, _
from multipli.models import StorageManager
from multipli.audio import SoundManager
from multipli.window import MultipliWindow
from multipli.preferences_dialog import PreferencesDialog


class MultipliApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id=__app_id__,
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.window = None

    def do_startup(self):
        Adw.Application.do_startup(self)

        # Initialiser les préférences de langue et son
        storage = StorageManager.get_instance()
        saved_lang = storage.settings.get("language", "fr")
        I18n.get_instance().set_language(saved_lang)

        sound_enabled = storage.settings.get("sound_enabled", True)
        SoundManager.get_instance().enabled = sound_enabled

        # Déclarer les actions de l'application
        self._setup_actions()

    def _setup_actions(self):
        # Action Préférences
        act_preferences = Gio.SimpleAction.new("preferences", None)
        act_preferences.connect("activate", self._on_preferences)
        self.add_action(act_preferences)

        # Action À propos
        act_about = Gio.SimpleAction.new("about", None)
        act_about.connect("activate", self._on_about)
        self.add_action(act_about)

        # Action Quitter
        act_quit = Gio.SimpleAction.new("quit", None)
        act_quit.connect("activate", lambda *_: self.quit())
        self.add_action(act_quit)

        self.set_accels_for_action("app.quit", ["<primary>q"])
        self.set_accels_for_action("app.preferences", ["<primary>comma"])

    def do_activate(self):
        if not self.window:
            self.window = MultipliWindow(application=self)
        self.window.present()

    def _on_preferences(self, action, param):
        if self.window:
            dlg = PreferencesDialog(self.window)
            dlg.present()

    def _on_about(self, action, param):
        if not self.window:
            return

        about = Adw.AboutDialog() if hasattr(Adw, 'AboutDialog') else Adw.AboutWindow()
        about.set_application_name(_("app_title"))
        about.set_version(__version__)
        about.set_developer_name("Conçu avec amour pour les enfants de CE1 à CM2")
        about.set_comments(_("settings_about_desc"))
        about.set_website("https://gitlab.gnome.org")
        about.set_issue_url("https://gitlab.gnome.org")
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_developers(["Papa & Antigravity"])
        about.set_artists(["GNOME Project"])
        about.set_translator_credits("Multipli i18n Team")
        about.set_application_icon("org.gnome.Multipli")

        if hasattr(about, 'present'):
            about.present(self.window)
        else:
            about.show()


def main():
    app = MultipliApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
