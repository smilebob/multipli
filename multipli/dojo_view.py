"""
Vue du Dojo libre d'entraînement personnalisé.
Permet de choisir précisément les tables, le type de questions et le mode de saisie.
"""

from typing import Callable, List
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from multipli.i18n import _


class DojoView(Gtk.Box):
    def __init__(self, on_start_dojo_callback: Callable[[dict], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.on_start_dojo = on_start_dojo_callback

        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)

        self.table_buttons: List[Gtk.ToggleButton] = []
        self._build_ui()

    def _build_ui(self):
        # En-tête
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header.set_halign(Gtk.Align.CENTER)

        self.title_lbl = Gtk.Label(label=_("nav_dojo"))
        self.title_lbl.add_css_class("title-2")

        self.subtitle_lbl = Gtk.Label(label="Entraîne-toi sur mesure sur les tables de ton choix !")
        self.subtitle_lbl.add_css_class("dim-label")

        header.append(self.title_lbl)
        header.append(self.subtitle_lbl)
        self.append(header)

        # Contenu dans un ScrolledWindow pour convenir à toutes les tailles d'écrans
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        clamp = Adw.Clamp()
        clamp.set_maximum_size(640)
        clamp.set_tightening_threshold(560)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.set_margin_top(12)
        content.set_margin_bottom(16)
        clamp.set_child(content)
        scroll.set_child(clamp)
        self.append(scroll)

        # 1. Sélection des tables
        tables_card = Adw.Bin()
        tables_card.add_css_class("card")
        tables_card.set_hexpand(True)

        t_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        t_box.set_margin_top(16)
        t_box.set_margin_bottom(16)
        t_box.set_margin_start(16)
        t_box.set_margin_end(16)

        self.t_title = Gtk.Label(label=_("dojo_choose_tables"))
        self.t_title.add_css_class("heading")
        self.t_title.set_halign(Gtk.Align.START)
        t_box.append(self.t_title)

        # Grille des tables 1 à 12
        grid_tables = Gtk.Grid()
        grid_tables.set_row_spacing(8)
        grid_tables.set_column_spacing(8)
        grid_tables.set_halign(Gtk.Align.CENTER)

        self.table_buttons = []
        for i in range(1, 13):
            btn = Gtk.ToggleButton(label=f"× {i}")
            btn.set_size_request(68, 42)
            btn.add_css_class("pill")
            if i in [2, 3, 4, 5]:  # Actives par défaut
                btn.set_active(True)
            self.table_buttons.append(btn)
            r = (i - 1) // 4
            c = (i - 1) % 4
            grid_tables.attach(btn, c, r, 1, 1)

        t_box.append(grid_tables)

        # Raccourcis de sélection
        quick_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        quick_box.set_halign(Gtk.Align.CENTER)

        self.btn_select_all = Gtk.Button(label=_("dojo_select_all"))
        self.btn_select_all.add_css_class("flat")
        self.btn_select_all.connect("clicked", lambda _: [b.set_active(True) for b in self.table_buttons])

        self.btn_deselect_all = Gtk.Button(label=_("dojo_deselect_all"))
        self.btn_deselect_all.add_css_class("flat")
        self.btn_deselect_all.connect("clicked", lambda _: [b.set_active(False) for b in self.table_buttons])

        quick_box.append(self.btn_select_all)
        quick_box.append(self.btn_deselect_all)
        t_box.append(quick_box)

        tables_card.set_child(t_box)
        content.append(tables_card)

        # 2. Options de jeu (Mode de saisie, Type de calculs, Nombre de questions)
        options_card = Adw.Bin()
        options_card.add_css_class("card")
        options_card.set_hexpand(True)

        opt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        opt_box.set_margin_top(16)
        opt_box.set_margin_bottom(16)
        opt_box.set_margin_start(16)
        opt_box.set_margin_end(16)

        # Mode de saisie
        mode_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.mode_lbl = Gtk.Label(label=_("dojo_input_mode"))
        self.mode_lbl.add_css_class("heading")
        self.mode_lbl.set_halign(Gtk.Align.START)
        mode_box.append(self.mode_lbl)

        mode_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.radio_qcm = Gtk.ToggleButton(label=_("dojo_mode_qcm"))
        self.radio_qcm.set_active(True)
        self.radio_qcm.add_css_class("pill")

        self.radio_pad = Gtk.ToggleButton(label=_("dojo_mode_keypad"), group=self.radio_qcm)
        self.radio_pad.add_css_class("pill")

        mode_btns.append(self.radio_qcm)
        mode_btns.append(self.radio_pad)
        mode_box.append(mode_btns)
        opt_box.append(mode_box)

        # Type de calculs
        type_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.type_lbl = Gtk.Label(label=_("dojo_question_type"))
        self.type_lbl.add_css_class("heading")
        self.type_lbl.set_halign(Gtk.Align.START)
        type_box.append(self.type_lbl)

        type_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.radio_direct = Gtk.ToggleButton(label="Direct (7 × 8)")
        self.radio_direct.set_active(True)
        self.radio_direct.add_css_class("pill")

        self.radio_missing = Gtk.ToggleButton(label="À trous (7 × ?)", group=self.radio_direct)
        self.radio_missing.add_css_class("pill")

        self.radio_mixed = Gtk.ToggleButton(label="Mélange", group=self.radio_direct)
        self.radio_mixed.add_css_class("pill")

        type_btns.append(self.radio_direct)
        type_btns.append(self.radio_missing)
        type_btns.append(self.radio_mixed)
        type_box.append(type_btns)
        opt_box.append(type_box)

        # Nombre de questions
        count_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.count_lbl = Gtk.Label(label=_("dojo_count_label"))
        self.count_lbl.add_css_class("heading")
        self.count_lbl.set_halign(Gtk.Align.START)
        count_box.append(self.count_lbl)

        count_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.btn_q10 = Gtk.ToggleButton(label="10")
        self.btn_q10.set_active(True)
        self.btn_q10.add_css_class("pill")

        self.btn_q15 = Gtk.ToggleButton(label="15", group=self.btn_q10)
        self.btn_q15.add_css_class("pill")

        self.btn_q20 = Gtk.ToggleButton(label="20", group=self.btn_q10)
        self.btn_q20.add_css_class("pill")

        count_btns.append(self.btn_q10)
        count_btns.append(self.btn_q15)
        count_btns.append(self.btn_q20)
        count_box.append(count_btns)
        opt_box.append(count_box)

        options_card.set_child(opt_box)
        content.append(options_card)

        # Bouton Démarrer
        self.btn_start = Gtk.Button(label=_("btn_start"))
        self.btn_start.add_css_class("pill")
        self.btn_start.add_css_class("suggested-action")
        self.btn_start.set_size_request(240, 50)
        self.btn_start.set_halign(Gtk.Align.CENTER)
        self.btn_start.connect("clicked", self._on_start_clicked)
        content.append(self.btn_start)

    def _on_start_clicked(self, btn):
        selected_tables = [i + 1 for i, b in enumerate(self.table_buttons) if b.get_active()]
        if not selected_tables:
            # Si aucune sélectionnée, prendre la table de 2 par défaut
            selected_tables = [2]
            self.table_buttons[1].set_active(True)

        input_mode = "qcm" if self.radio_qcm.get_active() else "keypad"

        if self.radio_direct.get_active():
            q_types = ["direct"]
        elif self.radio_missing.get_active():
            q_types = ["missing_factor_a", "missing_factor_b"]
        else:
            q_types = ["direct", "missing_factor_a", "missing_factor_b"]

        count = 10
        if self.btn_q15.get_active():
            count = 15
        elif self.btn_q20.get_active():
            count = 20

        config = {
            "tables": selected_tables,
            "total_questions": count,
            "input_mode": input_mode,
            "question_types": q_types,
            "level_id": None,
        }
        self.on_start_dojo(config)

    def update_i18n(self):
        self.title_lbl.set_label(_("nav_dojo"))
        self.t_title.set_label(_("dojo_choose_tables"))
        self.btn_select_all.set_label(_("dojo_select_all"))
        self.btn_deselect_all.set_label(_("dojo_deselect_all"))
        self.mode_lbl.set_label(_("dojo_input_mode"))
        self.radio_qcm.set_label(_("dojo_mode_qcm"))
        self.radio_pad.set_label(_("dojo_mode_keypad"))
        self.type_lbl.set_label(_("dojo_question_type"))
        self.count_lbl.set_label(_("dojo_count_label"))
        self.btn_start.set_label(_("btn_start"))
