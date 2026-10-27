"""
Fenêtre principale native GNOME pour l'application Multipli.
Conçue selon les GNOME Human Interface Guidelines (HIG) avec Libadwaita.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject

from multipli.i18n import I18n, _
from multipli.models import StorageManager
from multipli.audio import SoundManager
from multipli.adventure_view import AdventureView
from multipli.dojo_view import DojoView
from multipli.time_attack_view import TimeAttackView
from multipli.pythagoras import PythagorasView
from multipli.stats_view import StatsView
from multipli.game_view import GameView
from multipli.profiles_dialog import ProfilesDialog
from multipli.preferences_dialog import PreferencesDialog


CUSTOM_CSS = """
/* Typographie et styles éducatifs GNOME */
.calc-question {
    font-size: 38px;
    font-weight: 800;
    margin: 12px;
}

.calc-input-display {
    font-size: 32px;
    font-weight: 700;
    min-height: 48px;
    padding: 4px 16px;
    border-radius: 12px;
    background: alpha(@accent_color, 0.15);
    color: @accent_color;
}

.qcm-button {
    font-size: 22px;
    font-weight: 700;
    border-radius: 14px;
    padding: 12px;
}

.qcm-correct {
    background-color: #2ec27e;
    color: white;
}

.qcm-wrong {
    background-color: #e01b24;
    color: white;
}

.keypad-button {
    font-size: 20px;
    font-weight: 700;
    border-radius: 12px;
}

.keypad-button-clear {
    font-size: 18px;
    font-weight: bold;
    border-radius: 12px;
}

.keypad-button-ok {
    font-size: 22px;
    font-weight: 800;
    border-radius: 12px;
}

.feedback-success {
    color: #2ec27e;
    font-weight: bold;
}

.feedback-error {
    color: #e01b24;
    font-weight: bold;
}

.adventure-badge {
    font-size: 42px;
    padding: 8px;
}

.adventure-stars {
    font-size: 18px;
    color: #f6d32d;
    margin-top: 4px;
}

.chrono-icon {
    font-size: 56px;
}

.stats-avatar {
    font-size: 48px;
}

.trophy-icon {
    font-size: 26px;
    padding: 4px;
}

.trophy-icon-locked {
    font-size: 26px;
    opacity: 0.4;
    padding: 4px;
}

/* Table de Pythagore */
.selected-cell {
    background-color: @accent_color;
    color: @accent_fg_color;
    font-weight: 800;
    border-radius: 8px;
}

.sym-cell {
    background-color: #9141ac;
    color: white;
    font-weight: 800;
    border-radius: 8px;
}

.square-cell {
    background-color: alpha(#e5a50a, 0.25);
    font-weight: bold;
}

.highlight-line {
    background-color: alpha(@accent_color, 0.2);
}
"""


class MultipliWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title(_("app_title"))
        self.set_default_size(880, 700)
        self.set_size_request(380, 500)

        # Appliquer les styles CSS
        self._apply_css()

        # Configurer l'écoute des changements de langue
        I18n.get_instance().add_listener(self._on_language_changed)

        self._build_ui()
        self._update_profile_button()

    def _apply_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_string(CUSTOM_CSS)
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _build_ui(self):
        self.toolbar_view = Adw.ToolbarView()
        self.set_content(self.toolbar_view)

        # HeaderBar principale
        self.header_bar = Adw.HeaderBar()

        # Bouton profil enfant à gauche
        self.btn_profile = Gtk.Button()
        self.btn_profile.add_css_class("flat")
        self.btn_profile.connect("clicked", self._open_profiles_dialog)
        self.header_bar.pack_start(self.btn_profile)

        # Sélecteur de vues au centre
        self.view_stack = Adw.ViewStack()
        self.view_switcher_title = Adw.ViewSwitcherTitle(stack=self.view_stack)
        self.header_bar.set_title_widget(self.view_switcher_title)

        # Menu hamburger à droite
        menu_btn = Gtk.MenuButton()
        menu_btn.set_icon_name("open-menu-symbolic")
        menu = Gio.Menu()
        menu.append(_("btn_settings"), "app.preferences")
        menu.append(_("btn_about"), "app.about")
        menu_btn.set_menu_model(menu)
        self.header_bar.pack_end(menu_btn)

        self.toolbar_view.add_top_bar(self.header_bar)

        # Vues du jeu
        self.adventure_view = AdventureView(self._start_adventure_level)
        self.page_adventure = self.view_stack.add_titled_with_icon(
            self.adventure_view, "adventure", _("nav_adventure"), "trophy-gold-symbolic"
        )

        self.dojo_view = DojoView(self._start_dojo_game)
        self.page_dojo = self.view_stack.add_titled_with_icon(
            self.dojo_view, "dojo", _("nav_dojo"), "accessories-calculator-symbolic"
        )

        self.chrono_view = TimeAttackView(self._on_game_back)
        self.page_chrono = self.view_stack.add_titled_with_icon(
            self.chrono_view, "chrono", _("nav_chrono"), "alarm-symbolic"
        )

        self.pythagore_view = PythagorasView()
        self.page_pythagore = self.view_stack.add_titled_with_icon(
            self.pythagore_view, "pythagore", _("nav_pythagore"), "view-grid-symbolic"
        )

        self.stats_view = StatsView()
        self.page_stats = self.view_stack.add_titled_with_icon(
            self.stats_view, "stats", _("nav_stats"), "user-bookmarks-symbolic"
        )

        # Vue de partie active (s'affiche par-dessus quand un jeu est lancé)
        self.game_view = GameView(self._on_game_back)
        self.page_game = self.view_stack.add_named(self.game_view, "game")

        # Attacher le ViewStack au contenu central du ToolbarView
        self.toolbar_view.set_content(self.view_stack)

        # Sélectionner la première vue par défaut
        self.view_stack.set_visible_child_name("adventure")

        # Barre inférieure pour écrans étroits
        self.bottom_bar = Adw.ViewSwitcherBar(stack=self.view_stack)
        self.view_switcher_title.bind_property(
            "title-visible",
            self.bottom_bar,
            "reveal",
            GObject.BindingFlags.SYNC_CREATE
        )
        self.toolbar_view.add_bottom_bar(self.bottom_bar)

        # Écouter le changement d'onglet pour rafraîchir les stats
        self.view_stack.connect("notify::visible-child", self._on_tab_changed)

    def _start_adventure_level(self, level_config: dict):
        self.view_switcher_title.set_visible(False)
        self.bottom_bar.set_visible(False)
        self.game_view.start_game(
            tables=level_config["tables"],
            total_questions=level_config["count"],
            input_mode=level_config["input_mode"],
            question_types=level_config["types"],
            level_id=level_config["id"],
        )
        self.view_stack.set_visible_child_name("game")

    def _start_dojo_game(self, dojo_config: dict):
        self.view_switcher_title.set_visible(False)
        self.bottom_bar.set_visible(False)
        self.game_view.start_game(
            tables=dojo_config["tables"],
            total_questions=dojo_config["total_questions"],
            input_mode=dojo_config["input_mode"],
            question_types=dojo_config["question_types"],
            level_id=None,
        )
        self.view_stack.set_visible_child_name("game")

    def _on_game_back(self):
        self.view_switcher_title.set_visible(True)
        self.bottom_bar.set_visible(True)
        self.view_stack.set_visible_child_name("adventure")
        self.adventure_view.refresh_levels()
        self.stats_view.refresh()

    def _on_tab_changed(self, stack, param):
        name = stack.get_visible_child_name()
        if name == "stats":
            self.stats_view.refresh()
        elif name == "adventure":
            self.adventure_view.refresh_levels()
        elif name == "chrono":
            self.chrono_view.reset_to_intro()

    def _update_profile_button(self):
        p = StorageManager.get_instance().get_active_profile()
        self.btn_profile.set_label(f"{p.avatar}  {p.name}")

    def _open_profiles_dialog(self, btn):
        def on_changed():
            self._update_profile_button()
            self.adventure_view.refresh_levels()
            self.stats_view.refresh()
            self.chrono_view.reset_to_intro()

        dlg = ProfilesDialog(self, on_changed)
        dlg.present()

    def _on_language_changed(self, lang_code: str):
        self.set_title(_("app_title"))
        self.page_adventure.set_title(_("nav_adventure"))
        self.page_dojo.set_title(_("nav_dojo"))
        self.page_chrono.set_title(_("nav_chrono"))
        self.page_pythagore.set_title(_("nav_pythagore"))
        self.page_stats.set_title(_("nav_stats"))

        self.adventure_view.update_i18n()
        self.dojo_view.update_i18n()
        self.chrono_view.update_i18n()
        self.pythagore_view.update_i18n()
        self.stats_view.update_i18n()
