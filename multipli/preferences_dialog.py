"""
Dialogue des Préférences de l'application (Langue, Effets sonores, Ajout de langues).
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from multipli.i18n import I18n, _
from multipli.audio import SoundManager
from multipli.models import StorageManager


class PreferencesDialog(Adw.PreferencesWindow):
    def __init__(self, parent_window: Gtk.Window):
        super().__init__()
        self.set_transient_for(parent_window)
        self.set_modal(True)
        self.set_title(_("settings_title"))
        self.set_default_size(540, 500)

        self._build_ui()

    def _build_ui(self):
        page = Adw.PreferencesPage()
        self.add(page)

        # Groupe 1 : Apparence & Langue
        group_general = Adw.PreferencesGroup(title="Général")
        page.add(group_general)

        # Sélecteur de langue dynamique
        i18n = I18n.get_instance()
        available_langs = i18n.get_available_languages()

        # Modèle pour le ComboRow
        string_list = Gtk.StringList()
        current_idx = 0
        self.lang_codes = []

        for idx, (code, name, flag) in enumerate(available_langs):
            string_list.append(f"{flag}  {name} ({code})")
            self.lang_codes.append(code)
            if code == i18n.current_lang:
                current_idx = idx

        self.lang_combo = Adw.ComboRow(
            title=_("settings_lang"),
            subtitle=_("settings_lang_desc"),
            model=string_list,
        )
        self.lang_combo.set_selected(current_idx)
        self.lang_combo.connect("notify::selected", self._on_lang_changed)
        group_general.add(self.lang_combo)

        # Effets sonores
        storage = StorageManager.get_instance()
        sound_enabled = storage.settings.get("sound_enabled", True)

        self.sound_switch = Adw.SwitchRow(
            title=_("settings_sound"),
            subtitle=_("settings_sound_desc"),
        )
        self.sound_switch.set_active(sound_enabled)
        self.sound_switch.connect("notify::active", self._on_sound_toggled)
        group_general.add(self.sound_switch)

        # Groupe 2 : Multilingue & Contribution facile
        group_i18n_info = Adw.PreferencesGroup(
            title=_("settings_i18n_title"),
            description=_("settings_i18n_desc")
        )
        page.add(group_i18n_info)

        locales_path = i18n.locales_dir
        info_row = Adw.ActionRow(
            title=_("settings_locales_folder"),
            subtitle=f"{locales_path}",
        )
        info_row.set_subtitle_selectable(True)
        group_i18n_info.add(info_row)

        # Groupe 3 : Licence & Code source Open Source
        group_legal = Adw.PreferencesGroup(
            title=_("settings_legal_title"),
            description=_("settings_legal_desc")
        )
        page.add(group_legal)

        license_row = Adw.ActionRow(
            title="Apache License 2.0",
            subtitle=_("settings_license_subtitle"),
        )
        group_legal.add(license_row)

    def _on_lang_changed(self, combo, param):
        idx = combo.get_selected()
        if 0 <= idx < len(self.lang_codes):
            code = self.lang_codes[idx]
            storage = StorageManager.get_instance()
            storage.settings["language"] = code
            storage.save()
            I18n.get_instance().set_language(code)
            self.set_title(_("settings_title"))

    def _on_sound_toggled(self, switch, param):
        is_active = switch.get_active()
        SoundManager.get_instance().enabled = is_active
        storage = StorageManager.get_instance()
        storage.settings["sound_enabled"] = is_active
        storage.save()
        if is_active:
            SoundManager.get_instance().play_success()
