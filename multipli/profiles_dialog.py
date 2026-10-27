"""
Dialogue Adwaita pour gérer les profils des enfants :
sélection, édition (prénom, avatar, niveau de départ CE1-CM2), création et suppression.
"""

from typing import Callable, Optional
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from multipli.i18n import _
from multipli.models import StorageManager, Profile


LEVEL_OPTIONS = [
    ("ce1", "🌱 CE1 (Tables 2, 5, 10)"),
    ("ce2", "🌿 CE2 (Tables 3, 4, 5, 6)"),
    ("cm1", "⚡ CM1 (Tables 6, 7, 8, 9)"),
    ("cm2", "👑 CM2 (Toutes les tables 2 à 12)"),
]


class EditProfileDialog(Adw.PreferencesWindow):
    """Fenêtre de modification d'un profil existant."""
    def __init__(self, parent_window: Gtk.Window, profile: Profile, on_saved_cb: Callable[[], None]):
        super().__init__()
        self.set_transient_for(parent_window)
        self.set_modal(True)
        self.set_title(_("profile_edit_title"))
        self.set_default_size(540, 560)

        self.profile = profile
        self.on_saved = on_saved_cb

        self.avatars = ["🦊", "🐼", "🦉", "🐱", "🦁", "🦄", "🚀", "⭐"]
        self.selected_avatar = profile.avatar
        self.avatar_btns = []

        self._build_ui()

    def _build_ui(self):
        page = Adw.PreferencesPage()
        self.add(page)

        # 1. Groupe Informations de base
        group_info = Adw.PreferencesGroup(title=_("profile_edit_title"))
        page.add(group_info)

        self.entry_name = Adw.EntryRow(title=_("profile_name"))
        self.entry_name.set_text(self.profile.name)
        group_info.add(self.entry_name)

        # Niveau de départ
        level_list = Gtk.StringList()
        current_idx = 0
        self.level_codes = []

        for idx, (code, label) in enumerate(LEVEL_OPTIONS):
            level_list.append(label)
            self.level_codes.append(code)
            if code == self.profile.start_level:
                current_idx = idx

        self.level_combo = Adw.ComboRow(
            title=_("profile_start_level"),
            subtitle=_("profile_start_level_desc"),
            model=level_list,
        )
        self.level_combo.set_selected(current_idx)
        group_info.add(self.level_combo)

        # 2. Groupe Avatar (présenté dans un cadre dédié et centré)
        group_avatar = Adw.PreferencesGroup(title=_("profile_avatar"))
        page.add(group_avatar)

        avatar_card = Adw.Bin()
        avatar_card.add_css_class("card")
        avatar_card.set_hexpand(True)

        avatar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        avatar_box.set_halign(Gtk.Align.CENTER)
        avatar_box.set_margin_top(12)
        avatar_box.set_margin_bottom(12)
        avatar_box.set_margin_start(12)
        avatar_box.set_margin_end(12)

        self.avatar_btns = []
        for av in self.avatars:
            b = Gtk.ToggleButton(label=av)
            b.add_css_class("flat")
            b.set_size_request(46, 46)
            if av == self.selected_avatar:
                b.set_active(True)
            self.avatar_btns.append(b)

            def make_handler(chosen, btn):
                return lambda _: self._select_avatar(chosen, btn)

            b.connect("clicked", make_handler(av, b))
            avatar_box.append(b)

        avatar_card.set_child(avatar_box)
        group_avatar.add(avatar_card)

        # 3. Bouton Enregistrer
        group_action = Adw.PreferencesGroup()
        page.add(group_action)

        save_row = Adw.ActionRow()
        btn_save = Gtk.Button(label=_("btn_save"))
        btn_save.add_css_class("suggested-action")
        btn_save.add_css_class("pill")
        btn_save.connect("clicked", self._on_save_clicked)
        save_row.add_suffix(btn_save)
        group_action.add(save_row)

    def _select_avatar(self, chosen: str, active_btn: Gtk.ToggleButton):
        self.selected_avatar = chosen
        for b in self.avatar_btns:
            if b != active_btn:
                b.set_active(False)
        active_btn.set_active(True)

    def _on_save_clicked(self, btn):
        name = self.entry_name.get_text().strip()
        if not name:
            name = self.profile.name

        sel_idx = self.level_combo.get_selected()
        start_level = self.level_codes[sel_idx] if 0 <= sel_idx < len(self.level_codes) else "ce1"

        StorageManager.get_instance().update_profile(
            self.profile.id,
            name=name,
            avatar=self.selected_avatar,
            start_level=start_level,
        )
        self.on_saved()
        self.close()


class ProfilesDialog(Adw.PreferencesWindow):
    """Fenêtre de gestion et sélection des profils."""
    def __init__(self, parent_window: Gtk.Window, on_profile_changed_cb: Callable[[], None]):
        super().__init__()
        self.set_transient_for(parent_window)
        self.set_modal(True)
        self.set_title(_("profiles_manage"))
        self.set_default_size(560, 620)

        self.on_profile_changed = on_profile_changed_cb
        self.avatars = ["🦊", "🐼", "🦉", "🐱", "🦁", "🦄", "🚀", "⭐"]
        self.selected_avatar = "🦊"
        self.avatar_btns = []

        self._build_ui()

    def _build_ui(self):
        page = Adw.PreferencesPage()
        self.add(page)

        # Groupe 1 : Profils existants
        self.group_profiles = Adw.PreferencesGroup(title=_("profiles_manage"))
        page.add(self.group_profiles)
        self._populate_profiles()

        # Groupe 2 : Créer un nouveau profil
        group_new = Adw.PreferencesGroup(title=_("btn_add_player"))
        page.add(group_new)

        self.entry_name = Adw.EntryRow(title=_("profile_name"))
        group_new.add(self.entry_name)

        # Choix du niveau de départ
        level_list = Gtk.StringList()
        self.new_level_codes = []
        for code, label in LEVEL_OPTIONS:
            level_list.append(label)
            self.new_level_codes.append(code)

        self.new_level_combo = Adw.ComboRow(
            title=_("profile_start_level"),
            subtitle=_("profile_start_level_desc"),
            model=level_list,
        )
        self.new_level_combo.set_selected(0)
        group_new.add(self.new_level_combo)

        # Groupe 3 : Choix de l'avatar pour le nouveau profil
        group_avatar = Adw.PreferencesGroup(title=_("profile_avatar"))
        page.add(group_avatar)

        avatar_card = Adw.Bin()
        avatar_card.add_css_class("card")
        avatar_card.set_hexpand(True)

        avatar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        avatar_box.set_halign(Gtk.Align.CENTER)
        avatar_box.set_margin_top(12)
        avatar_box.set_margin_bottom(12)
        avatar_box.set_margin_start(12)
        avatar_box.set_margin_end(12)

        self.avatar_btns = []
        for av in self.avatars:
            b = Gtk.ToggleButton(label=av)
            b.add_css_class("flat")
            b.set_size_request(46, 46)
            if av == self.selected_avatar:
                b.set_active(True)
            self.avatar_btns.append(b)

            def make_handler(chosen, btn):
                return lambda _: self._select_avatar(chosen, btn)

            b.connect("clicked", make_handler(av, b))
            avatar_box.append(b)

        avatar_card.set_child(avatar_box)
        group_avatar.add(avatar_card)

        # Groupe 4 : Bouton Ajouter
        group_action = Adw.PreferencesGroup()
        page.add(group_action)

        add_btn_row = Adw.ActionRow()
        btn_add = Gtk.Button(label=_("profile_create"))
        btn_add.add_css_class("suggested-action")
        btn_add.add_css_class("pill")
        btn_add.connect("clicked", self._on_add_profile)
        add_btn_row.add_suffix(btn_add)
        group_action.add(add_btn_row)

    def _populate_profiles(self):
        storage = StorageManager.get_instance()
        active_id = storage.active_profile_id

        level_names = {
            "ce1": "🌱 CE1",
            "ce2": "🌿 CE2",
            "cm1": "⚡ CM1",
            "cm2": "👑 CM2",
        }

        for profile in storage.profiles:
            row = Adw.ActionRow()
            row.set_title(f"{profile.avatar}  {profile.name}")
            total_stars = sum(profile.stars.values())
            grade_str = level_names.get(profile.start_level, "🌱 CE1")
            row.set_subtitle(f"{grade_str} • {total_stars} ⭐ • Record chrono : {profile.chrono_best} pts")

            is_active = (profile.id == active_id)

            # 1. Bouton Modifier (Crayon)
            btn_edit = Gtk.Button.new_from_icon_name("document-edit-symbolic")
            btn_edit.add_css_class("flat")
            btn_edit.set_tooltip_text(_("btn_edit"))

            def make_edit_handler(p):
                return lambda _: self._open_edit_dialog(p)

            btn_edit.connect("clicked", make_edit_handler(profile))
            row.add_suffix(btn_edit)

            # 2. Bouton Sélectionner / Témoin actif
            if is_active:
                check_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
                check_icon.add_css_class("accent")
                row.add_suffix(check_icon)
            else:
                btn_select = Gtk.Button(label="Choisir")
                btn_select.add_css_class("pill")
                btn_select.add_css_class("flat")

                def make_select_handler(p_id):
                    return lambda _: self._on_select_profile(p_id)

                btn_select.connect("clicked", make_select_handler(profile.id))
                row.add_suffix(btn_select)

            # 3. Bouton Supprimer
            if len(storage.profiles) > 1 and not is_active:
                btn_del = Gtk.Button.new_from_icon_name("user-trash-symbolic")
                btn_del.add_css_class("flat")
                btn_del.add_css_class("destructive-action")

                def make_del_handler(p_id):
                    return lambda _: self._on_delete_profile(p_id)

                btn_del.connect("clicked", make_del_handler(profile.id))
                row.add_suffix(btn_del)

            self.group_profiles.add(row)

    def _open_edit_dialog(self, profile: Profile):
        def on_saved():
            self.on_profile_changed()
            self.close()

        dlg = EditProfileDialog(self, profile, on_saved)
        dlg.present()

    def _select_avatar(self, chosen: str, active_btn: Gtk.ToggleButton):
        self.selected_avatar = chosen
        for b in self.avatar_btns:
            if b != active_btn:
                b.set_active(False)
        active_btn.set_active(True)

    def _on_select_profile(self, profile_id: str):
        StorageManager.get_instance().set_active_profile(profile_id)
        self.on_profile_changed()
        self.close()

    def _on_delete_profile(self, profile_id: str):
        StorageManager.get_instance().delete_profile(profile_id)
        self.on_profile_changed()
        self.close()

    def _on_add_profile(self, btn):
        name = self.entry_name.get_text().strip()
        if not name:
            name = "Élève"

        sel_idx = self.new_level_combo.get_selected()
        start_level = self.new_level_codes[sel_idx] if 0 <= sel_idx < len(self.new_level_codes) else "ce1"

        StorageManager.get_instance().add_profile(name, self.selected_avatar, start_level=start_level)
        self.entry_name.set_text("")
        self.on_profile_changed()
        self.close()
