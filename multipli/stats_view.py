"""
Vue des Progrès, Statistiques détaillées par table et Galerie des Trophées.
Permet d'identifier instantanément les tables à réviser.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from multipli.i18n import _
from multipli.models import StorageManager


class StatsView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)

        self._build_ui()

    def _build_ui(self):
        # En-tête
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header.set_halign(Gtk.Align.CENTER)

        self.title_lbl = Gtk.Label(label=_("stats_title"))
        self.title_lbl.add_css_class("title-2")
        header.append(self.title_lbl)
        self.append(header)

        # ScrolledWindow pour faire défiler toutes les tables et trophées
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.content_box.set_margin_start(20)
        self.content_box.set_margin_end(20)
        self.content_box.set_halign(Gtk.Align.CENTER)

        scroll.set_child(self.content_box)
        self.append(scroll)

        self.refresh()

    def refresh(self):
        # Nettoyer l'ancien contenu
        child = self.content_box.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self.content_box.remove(child)
            child = nxt

        profile = StorageManager.get_instance().get_active_profile()

        # 1. Carte résumé du profil
        summary_card = Adw.Bin()
        summary_card.add_css_class("card")
        summary_card.set_size_request(600, -1)

        sum_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        sum_box.set_margin_top(16)
        sum_box.set_margin_bottom(16)
        sum_box.set_margin_start(20)
        sum_box.set_margin_end(20)

        # Avatar
        avatar_lbl = Gtk.Label(label=profile.avatar)
        avatar_lbl.add_css_class("stats-avatar")
        sum_box.append(avatar_lbl)

        # Statistiques globales
        stats_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        stats_info.set_hexpand(True)

        p_name = Gtk.Label(label=profile.name)
        p_name.set_halign(Gtk.Align.START)
        p_name.add_css_class("title-3")
        stats_info.append(p_name)

        total_ans = profile.total_answered
        accuracy = int((profile.total_correct / total_ans * 100)) if total_ans > 0 else 0
        total_stars = sum(profile.stars.values())

        p_acc = Gtk.Label(label=_("stats_accuracy", rate=accuracy))
        p_acc.set_halign(Gtk.Align.START)
        p_acc.add_css_class("dim-label")

        p_stars = Gtk.Label(label=_("stats_stars_collected", stars=total_stars) + f" ⭐ • Chrono : {profile.chrono_best} pts ⚡")
        p_stars.set_halign(Gtk.Align.START)
        p_stars.add_css_class("dim-label")

        stats_info.append(p_acc)
        stats_info.append(p_stars)
        sum_box.append(stats_info)

        summary_card.set_child(sum_box)
        self.content_box.append(summary_card)

        # 2. Maîtrise des tables de 1 à 12
        tables_card = Adw.Bin()
        tables_card.add_css_class("card")
        tables_card.set_size_request(600, -1)

        tb_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tb_box.set_margin_top(16)
        tb_box.set_margin_bottom(16)
        tb_box.set_margin_start(20)
        tb_box.set_margin_end(20)

        tb_title = Gtk.Label(label=_("stats_per_table"))
        tb_title.set_halign(Gtk.Align.START)
        tb_title.add_css_class("heading")
        tb_box.append(tb_title)

        grid_stats = Gtk.Grid()
        grid_stats.set_row_spacing(8)
        grid_stats.set_column_spacing(16)

        for i in range(1, 13):
            t_key = str(i)
            t_data = profile.table_stats.get(t_key, {"correct": 0, "total": 0})
            total = t_data.get("total", 0)
            correct = t_data.get("correct", 0)
            rate = int(correct / total * 100) if total > 0 else 0

            # Nom table
            lbl_name = Gtk.Label(label=f"Table de {i}")
            lbl_name.set_halign(Gtk.Align.START)
            lbl_name.set_size_request(90, -1)
            lbl_name.add_css_class("caption")

            # Barre de progression
            pbar = Gtk.ProgressBar()
            pbar.set_fraction(rate / 100.0)
            pbar.set_hexpand(True)
            pbar.set_size_request(160, -1)

            # Badge textuel
            if total == 0:
                badge = Gtk.Label(label="-")
                badge.add_css_class("dim-label")
            elif rate >= 80:
                badge = Gtk.Label(label=f"{rate}% ({correct}/{total}) ✓")
                badge.add_css_class("feedback-success")
            elif rate >= 50:
                badge = Gtk.Label(label=f"{rate}% ({correct}/{total})")
                badge.add_css_class("accent")
            else:
                badge = Gtk.Label(label=f"{rate}% " + _("stats_need_practice"))
                badge.add_css_class("feedback-error")

            badge.set_halign(Gtk.Align.END)
            badge.add_css_class("caption")

            row_idx = i - 1
            grid_stats.attach(lbl_name, 0, row_idx, 1, 1)
            grid_stats.attach(pbar, 1, row_idx, 1, 1)
            grid_stats.attach(badge, 2, row_idx, 1, 1)

        tb_box.append(grid_stats)
        tables_card.set_child(tb_box)
        self.content_box.append(tables_card)

        # 3. Trophées
        trophies_card = Adw.Bin()
        trophies_card.add_css_class("card")
        trophies_card.set_size_request(600, -1)

        tr_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tr_box.set_margin_top(16)
        tr_box.set_margin_bottom(16)
        tr_box.set_margin_start(20)
        tr_box.set_margin_end(20)

        tr_title = Gtk.Label(label=_("trophies_title"))
        tr_title.set_halign(Gtk.Align.START)
        tr_title.add_css_class("heading")
        tr_box.append(tr_title)

        trophies_def = [
            ("first_win", "🌱", _("trophy_first_win"), _("trophy_first_win_desc")),
            ("streak_10", "🔥", _("trophy_streak_10"), _("trophy_streak_10_desc")),
            ("chrono_15", "⚡", _("trophy_chrono_15"), _("trophy_chrono_15_desc")),
            ("all_stars_ce1", "🎓", _("trophy_all_stars_ce1"), _("trophy_all_stars_ce1_desc")),
            ("all_stars_cm2", "👑", _("trophy_all_stars_cm2"), _("trophy_all_stars_cm2_desc")),
        ]

        grid_tr = Gtk.Grid()
        grid_tr.set_row_spacing(10)
        grid_tr.set_column_spacing(14)

        for idx, (t_id, icon, title, desc) in enumerate(trophies_def):
            unlocked = t_id in profile.trophies

            t_icon_lbl = Gtk.Label(label=icon if unlocked else "🔒")
            t_icon_lbl.add_css_class("trophy-icon" if unlocked else "trophy-icon-locked")

            t_text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            t_title_lbl = Gtk.Label(label=title)
            t_title_lbl.set_halign(Gtk.Align.START)
            t_title_lbl.add_css_class("body")
            if not unlocked:
                t_title_lbl.add_css_class("dim-label")

            t_desc_lbl = Gtk.Label(label=desc)
            t_desc_lbl.set_halign(Gtk.Align.START)
            t_desc_lbl.add_css_class("caption")
            t_desc_lbl.add_css_class("dim-label")

            t_text_box.append(t_title_lbl)
            t_text_box.append(t_desc_lbl)

            grid_tr.attach(t_icon_lbl, 0, idx, 1, 1)
            grid_tr.attach(t_text_box, 1, idx, 1, 1)

        tr_box.append(grid_tr)
        trophies_card.set_child(tr_box)
        self.content_box.append(trophies_card)

    def update_i18n(self):
        self.title_lbl.set_label(_("stats_title"))
        self.refresh()
