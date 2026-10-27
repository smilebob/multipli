"""
Table de Pythagore interactive pour l'apprentissage visuel des multiplications.
Permet d'explorer les symétries commutatives (a × b = b × a) et les carrés.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Pango
from multipli.i18n import _


class PythagorasView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)

        self.max_factor = 10
        self.selected_row = 6
        self.selected_col = 7
        self.buttons = {}  # (r, c) -> Gtk.Button

        self._build_ui()
        self.highlight_cell(self.selected_row, self.selected_col)

    def _build_ui(self):
        # En-tête explicatif
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header_box.set_halign(Gtk.Align.CENTER)

        self.title_label = Gtk.Label(label=_("pythagore_title"))
        self.title_label.add_css_class("title-2")

        self.subtitle_label = Gtk.Label(label=_("pythagore_subtitle"))
        self.subtitle_label.add_css_class("dim-label")

        header_box.append(self.title_label)
        header_box.append(self.subtitle_label)
        self.append(header_box)

        # Contrôle de taille (10x10 ou 12x12)
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        controls_box.set_halign(Gtk.Align.CENTER)

        btn_10 = Gtk.ToggleButton(label="10 × 10")
        btn_10.set_active(True)
        btn_10.add_css_class("pill")

        btn_12 = Gtk.ToggleButton(label="12 × 12", group=btn_10)
        btn_12.add_css_class("pill")

        def on_size_toggled(btn):
            if btn_10.get_active():
                self.max_factor = 10
            else:
                self.max_factor = 12
            self._rebuild_grid()
            self.highlight_cell(min(self.selected_row, self.max_factor), min(self.selected_col, self.max_factor))

        btn_10.connect("toggled", on_size_toggled)
        controls_box.append(btn_10)
        controls_box.append(btn_12)
        self.append(controls_box)

        # Cartouche de résultat / explication visuelle
        info_clamp = Adw.Clamp()
        info_clamp.set_maximum_size(600)
        info_clamp.set_tightening_threshold(520)

        self.info_card = Adw.Bin()
        self.info_card.set_margin_start(16)
        self.info_card.set_margin_end(16)
        self.info_card.add_css_class("card")

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        info_box.set_margin_top(12)
        info_box.set_margin_bottom(12)
        info_box.set_margin_start(16)
        info_box.set_margin_end(16)
        info_box.set_halign(Gtk.Align.CENTER)

        self.calc_label = Gtk.Label()
        self.calc_label.add_css_class("title-1")
        self.calc_label.add_css_class("accent")

        self.explanation_label = Gtk.Label()
        self.explanation_label.add_css_class("body")

        info_box.append(self.calc_label)
        info_box.append(self.explanation_label)
        self.info_card.set_child(info_box)
        info_clamp.set_child(self.info_card)
        self.append(info_clamp)

        # Grille scrollable
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.grid_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.grid_container.set_halign(Gtk.Align.CENTER)
        self.grid_container.set_valign(Gtk.Align.CENTER)
        scroll.set_child(self.grid_container)
        self.append(scroll)

        self._rebuild_grid()

    def _rebuild_grid(self):
        # Vider la grille précédente
        child = self.grid_container.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.grid_container.remove(child)
            child = next_child

        self.buttons.clear()
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(4)
        self.grid.set_column_spacing(4)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.CENTER)

        # Coin haut gauche (symbole ×)
        corner_btn = Gtk.Button(label="×")
        corner_btn.set_sensitive(False)
        corner_btn.add_css_class("flat")
        corner_btn.set_size_request(42, 42)
        self.grid.attach(corner_btn, 0, 0, 1, 1)

        # En-têtes de colonnes
        for c in range(1, self.max_factor + 1):
            lbl = Gtk.Label(label=str(c))
            lbl.add_css_class("heading")
            lbl.set_size_request(42, 42)
            self.grid.attach(lbl, c, 0, 1, 1)

        # En-têtes de lignes et cellules de calcul
        for r in range(1, self.max_factor + 1):
            row_lbl = Gtk.Label(label=str(r))
            row_lbl.add_css_class("heading")
            row_lbl.set_size_request(42, 42)
            self.grid.attach(row_lbl, 0, r, 1, 1)

            for c in range(1, self.max_factor + 1):
                val = r * c
                btn = Gtk.Button(label=str(val))
                btn.set_size_request(42, 42)
                btn.add_css_class("flat")

                # Style spécifique pour la diagonale des carrés
                if r == c:
                    btn.add_css_class("square-cell")

                # Gestion du clic
                def make_click_handler(row, col):
                    return lambda b: self.highlight_cell(row, col)

                btn.connect("clicked", make_click_handler(r, c))
                self.buttons[(r, c)] = btn
                self.grid.attach(btn, c, r, 1, 1)

        self.grid_container.append(self.grid)

    def highlight_cell(self, row: int, col: int):
        self.selected_row = row
        self.selected_col = col

        # Réinitialiser les classes CSS des boutons
        for (r, c), btn in self.buttons.items():
            btn.remove_css_class("selected-cell")
            btn.remove_css_class("sym-cell")
            btn.remove_css_class("highlight-line")

            if r == self.selected_row and c == self.selected_col:
                btn.add_css_class("selected-cell")
            elif r == self.selected_col and c == self.selected_row:
                btn.add_css_class("sym-cell")
            elif r == self.selected_row or c == self.selected_col:
                btn.add_css_class("highlight-line")

        # Mise à jour des explications
        res = row * col
        self.calc_label.set_label(f"{row} × {col} = {res}")

        if row == col:
            self.explanation_label.set_label(
                _("pythagore_square", a=row, res=res)
            )
        else:
            self.explanation_label.set_label(
                _("pythagore_commutativity", a=row, b=col, res=res)
            )

    def update_i18n(self):
        self.title_label.set_label(_("pythagore_title"))
        self.subtitle_label.set_label(_("pythagore_subtitle"))
        self.highlight_cell(self.selected_row, self.selected_col)
