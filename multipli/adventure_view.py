"""
Vue du mode Aventure avec progression par niveau scolaire (CE1 -> CM2).
Chaque niveau propose un défi adapté et permet de gagner jusqu'à 3 étoiles.
"""

from typing import Callable
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from multipli.i18n import _
from multipli.models import StorageManager


class AdventureView(Gtk.Box):
    def __init__(self, on_start_level_callback: Callable[[dict], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.on_start_level = on_start_level_callback

        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)

        self._build_ui()

    def _build_ui(self):
        # En-tête
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header_box.set_halign(Gtk.Align.CENTER)

        self.title_lbl = Gtk.Label(label=_("nav_adventure"))
        self.title_lbl.add_css_class("title-2")
        self.subtitle_lbl = Gtk.Label(label="Progresse du CE1 au CM2 pour devenir le Grand Maître des tables !")
        self.subtitle_lbl.add_css_class("dim-label")

        header_box.append(self.title_lbl)
        header_box.append(self.subtitle_lbl)
        self.append(header_box)

        # Liste des niveaux dans un ScrolledWindow
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.levels_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.levels_container.set_margin_start(20)
        self.levels_container.set_margin_end(20)
        self.levels_container.set_margin_top(12)
        self.levels_container.set_margin_bottom(12)
        self.levels_container.set_halign(Gtk.Align.CENTER)

        scrolled.set_child(self.levels_container)
        self.append(scrolled)

        self.refresh_levels()

    def refresh_levels(self):
        # Nettoyer
        child = self.levels_container.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self.levels_container.remove(child)
            child = nxt

        profile = StorageManager.get_instance().get_active_profile()
        stars_dict = profile.stars

        levels_config = [
            {
                "id": "ce1",
                "title": _("mode_ce1_title"),
                "desc": _("mode_ce1_desc"),
                "badge": "🌱",
                "tables": [2, 5, 10],
                "input_mode": "qcm",
                "types": ["direct"],
                "count": 10,
                "unlocked": True,
            },
            {
                "id": "ce2",
                "title": _("mode_ce2_title"),
                "desc": _("mode_ce2_desc"),
                "badge": "🌿",
                "tables": [3, 4, 5, 6],
                "input_mode": "qcm",
                "types": ["direct"],
                "count": 10,
                "unlocked": stars_dict.get("ce1", 0) >= 1,
            },
            {
                "id": "cm1",
                "title": _("mode_cm1_title"),
                "desc": _("mode_cm1_desc"),
                "badge": "⚡",
                "tables": [6, 7, 8, 9],
                "input_mode": "keypad",
                "types": ["direct", "missing_factor_a", "missing_factor_b"],
                "count": 12,
                "unlocked": stars_dict.get("ce2", 0) >= 1,
            },
            {
                "id": "cm2",
                "title": _("mode_cm2_title"),
                "desc": _("mode_cm2_desc"),
                "badge": "👑",
                "tables": list(range(2, 13)),
                "input_mode": "keypad",
                "types": ["direct", "missing_factor_a", "missing_factor_b"],
                "count": 15,
                "unlocked": stars_dict.get("cm1", 0) >= 1,
            },
        ]

        for lvl in levels_config:
            card = self._create_level_card(lvl, stars_dict.get(lvl["id"], 0))
            self.levels_container.append(card)

    def _create_level_card(self, lvl: dict, stars: int) -> Gtk.Widget:
        bin_card = Adw.Bin()
        bin_card.add_css_class("card")
        bin_card.set_size_request(580, -1)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        # Badge émoji à gauche
        badge_lbl = Gtk.Label(label=lvl["badge"])
        badge_lbl.add_css_class("adventure-badge")
        box.append(badge_lbl)

        # Textes centraux
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        text_box.set_hexpand(True)

        title = Gtk.Label(label=lvl["title"])
        title.set_halign(Gtk.Align.START)
        title.add_css_class("title-3")

        desc = Gtk.Label(label=lvl["desc"])
        desc.set_halign(Gtk.Align.START)
        desc.set_wrap(True)
        desc.set_max_width_chars(38)
        desc.add_css_class("dim-label")

        # Étoiles gagnées
        stars_str = ("⭐ " * stars) + ("☆ " * (3 - stars))
        stars_lbl = Gtk.Label(label=stars_str.strip())
        stars_lbl.set_halign(Gtk.Align.START)
        stars_lbl.add_css_class("adventure-stars")

        text_box.append(title)
        text_box.append(desc)
        text_box.append(stars_lbl)
        box.append(text_box)

        # Action à droite
        action_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        action_box.set_valign(Gtk.Align.CENTER)

        if lvl["unlocked"]:
            btn = Gtk.Button(label=_("btn_start"))
            btn.add_css_class("pill")
            btn.add_css_class("suggested-action")
            btn.connect("clicked", lambda _, config=lvl: self.on_start_level(config))
            action_box.append(btn)
        else:
            lock_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            lock_icon = Gtk.Image.new_from_icon_name("changes-prevent-symbolic")
            lock_box.append(lock_icon)
            lock_lbl = Gtk.Label(label=_("level_locked"))
            lock_lbl.add_css_class("caption")
            lock_box.append(lock_lbl)
            action_box.append(lock_box)

        box.append(action_box)
        bin_card.set_child(box)
        return bin_card

    def update_i18n(self):
        self.title_lbl.set_label(_("nav_adventure"))
        self.refresh_levels()
