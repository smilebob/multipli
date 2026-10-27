"""
Mode Chrono 60 secondes : Course contre la montre pour tester ses réflexes.
"""

import random
from typing import Callable, List
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gdk

from multipli.i18n import _
from multipli.audio import SoundManager
from multipli.models import StorageManager
from multipli.game_view import Question


class TimeAttackView(Gtk.Box):
    def __init__(self, on_back_callback: Callable[[], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.on_back_callback = on_back_callback

        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)

        self.time_left = 60
        self.timer_source_id = None
        self.score = 0
        self.current_question: Question = None
        self.user_input_buffer = ""
        self.input_mode = "qcm"

        self._build_ui()
        self._setup_keyboard_events()

    def _setup_keyboard_events(self):
        controller = Gtk.EventControllerKey.new()
        controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(controller)

    def _on_key_pressed(self, controller, keyval, keycode, state):
        if self.stack.get_visible_child_name() != "playing":
            return False

        if self.input_mode == "qcm":
            qcm_keys = {
                Gdk.KEY_1: 0, Gdk.KEY_KP_1: 0, Gdk.KEY_ampersand: 0,
                Gdk.KEY_2: 1, Gdk.KEY_KP_2: 1, Gdk.KEY_eacute: 1,
                Gdk.KEY_3: 2, Gdk.KEY_KP_3: 2, Gdk.KEY_quotedbl: 2,
                Gdk.KEY_4: 3, Gdk.KEY_KP_4: 3, Gdk.KEY_apostrophe: 3,
            }
            if keyval in qcm_keys:
                idx = qcm_keys[keyval]
                if idx < len(self.qcm_buttons):
                    self._check_answer(self.qcm_options[idx])
                    return True
        else:
            digit_keys = {
                Gdk.KEY_0: "0", Gdk.KEY_KP_0: "0",
                Gdk.KEY_1: "1", Gdk.KEY_KP_1: "1",
                Gdk.KEY_2: "2", Gdk.KEY_KP_2: "2",
                Gdk.KEY_3: "3", Gdk.KEY_KP_3: "3",
                Gdk.KEY_4: "4", Gdk.KEY_KP_4: "4",
                Gdk.KEY_5: "5", Gdk.KEY_KP_5: "5",
                Gdk.KEY_6: "6", Gdk.KEY_KP_6: "6",
                Gdk.KEY_7: "7", Gdk.KEY_KP_7: "7",
                Gdk.KEY_8: "8", Gdk.KEY_KP_8: "8",
                Gdk.KEY_9: "9", Gdk.KEY_KP_9: "9",
            }
            if keyval in digit_keys:
                self._append_digit(digit_keys[keyval])
                return True
            elif keyval in (Gdk.KEY_BackSpace, Gdk.KEY_Delete):
                self._clear_input()
                return True
            elif keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
                self._submit_keypad()
                return True

        return False

    def _build_ui(self):
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        # 1. Écran d'accueil du Chrono
        self.intro_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.intro_box.set_valign(Gtk.Align.CENTER)
        self.intro_box.set_halign(Gtk.Align.CENTER)

        intro_icon = Gtk.Label(label="⏱️")
        intro_icon.add_css_class("chrono-icon")
        self.intro_box.append(intro_icon)

        self.intro_title = Gtk.Label(label=_("chrono_title"))
        self.intro_title.add_css_class("title-1")
        self.intro_box.append(self.intro_title)

        self.intro_desc = Gtk.Label(label=_("chrono_desc"))
        self.intro_desc.add_css_class("dim-label")
        self.intro_desc.set_wrap(True)
        self.intro_desc.set_max_width_chars(45)
        self.intro_box.append(self.intro_desc)

        # Carte record personnel
        record_card = Adw.Bin()
        record_card.add_css_class("card")
        r_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        r_box.set_margin_top(12)
        r_box.set_margin_bottom(12)
        r_box.set_margin_start(20)
        r_box.set_margin_end(20)

        r_icon = Gtk.Label(label="🏆")
        r_box.append(r_icon)
        self.best_label = Gtk.Label(label="")
        self.best_label.add_css_class("heading")
        r_box.append(self.best_label)
        record_card.set_child(r_box)
        self.intro_box.append(record_card)

        # Choix du mode de saisie
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        mode_box.set_halign(Gtk.Align.CENTER)

        self.btn_qcm_choice = Gtk.ToggleButton(label=_("dojo_mode_qcm"))
        self.btn_qcm_choice.set_active(True)
        self.btn_qcm_choice.add_css_class("pill")

        self.btn_pad_choice = Gtk.ToggleButton(label=_("dojo_mode_keypad"), group=self.btn_qcm_choice)
        self.btn_pad_choice.add_css_class("pill")

        mode_box.append(self.btn_qcm_choice)
        mode_box.append(self.btn_pad_choice)
        self.intro_box.append(mode_box)

        # Bouton départ
        self.btn_start = Gtk.Button(label=_("chrono_start_btn"))
        self.btn_start.add_css_class("pill")
        self.btn_start.add_css_class("suggested-action")
        self.btn_start.set_size_request(220, 54)
        self.btn_start.connect("clicked", self._on_start_chrono)
        self.intro_box.append(self.btn_start)

        self.stack.add_named(self.intro_box, "intro")

        # 2. Écran en cours de jeu
        self.play_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        # Barre supérieure avec temps restant et score
        top_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        top_bar.set_hexpand(True)

        self.btn_abort = Gtk.Button(label=_("btn_back"))
        self.btn_abort.add_css_class("flat")
        self.btn_abort.connect("clicked", self._abort_chrono)
        top_bar.append(self.btn_abort)

        self.time_label = Gtk.Label(label="⏱️ 60s")
        self.time_label.add_css_class("title-2")
        self.time_label.set_hexpand(True)
        self.time_label.set_halign(Gtk.Align.CENTER)
        top_bar.append(self.time_label)

        self.score_label = Gtk.Label(label="Score : 0")
        self.score_label.add_css_class("title-3")
        self.score_label.add_css_class("accent")
        top_bar.append(self.score_label)

        self.play_box.append(top_bar)

        self.time_progress = Gtk.ProgressBar()
        self.time_progress.set_fraction(1.0)
        self.play_box.append(self.time_progress)

        # Carte de calcul
        c_card = Adw.Bin()
        c_card.add_css_class("card")
        c_card.set_margin_top(12)
        c_card.set_margin_bottom(12)
        c_card.set_vexpand(True)
        c_card.set_valign(Gtk.Align.CENTER)

        c_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        c_box.set_margin_top(24)
        c_box.set_margin_bottom(24)
        c_box.set_margin_start(24)
        c_box.set_margin_end(24)
        c_box.set_halign(Gtk.Align.CENTER)

        self.q_label = Gtk.Label(label="--")
        self.q_label.add_css_class("calc-question")
        c_box.append(self.q_label)

        self.pad_display = Gtk.Label(label="_")
        self.pad_display.add_css_class("calc-input-display")
        c_box.append(self.pad_display)

        c_card.set_child(c_box)
        self.play_box.append(c_card)

        # Contrôles de saisie
        self.input_stack = Gtk.Stack()

        # QCM
        self.qcm_grid = Gtk.Grid()
        self.qcm_grid.set_row_spacing(10)
        self.qcm_grid.set_column_spacing(10)
        self.qcm_grid.set_halign(Gtk.Align.CENTER)

        self.qcm_buttons = []
        self.qcm_options = []
        for i in range(4):
            btn = Gtk.Button(label="--")
            btn.set_size_request(130, 52)
            btn.add_css_class("qcm-button")
            r = i // 2
            c = i % 2
            self.qcm_grid.attach(btn, c, r, 1, 1)
            self.qcm_buttons.append(btn)

        self.input_stack.add_named(self.qcm_grid, "qcm")

        # Pavé
        keypad_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        keypad_box.set_halign(Gtk.Align.CENTER)

        kp_grid = Gtk.Grid()
        kp_grid.set_row_spacing(6)
        kp_grid.set_column_spacing(6)

        for num in range(1, 10):
            r = (num - 1) // 3
            c = (num - 1) % 3
            b = Gtk.Button(label=str(num))
            b.set_size_request(64, 48)
            b.add_css_class("keypad-button")
            d = str(num)
            b.connect("clicked", lambda _, digit=d: self._append_digit(digit))
            kp_grid.attach(b, c, r, 1, 1)

        b_c = Gtk.Button(label="⌫")
        b_c.set_size_request(64, 48)
        b_c.add_css_class("keypad-button-clear")
        b_c.connect("clicked", lambda _: self._clear_input())
        kp_grid.attach(b_c, 0, 3, 1, 1)

        b_0 = Gtk.Button(label="0")
        b_0.set_size_request(64, 48)
        b_0.add_css_class("keypad-button")
        b_0.connect("clicked", lambda _: self._append_digit("0"))
        kp_grid.attach(b_0, 1, 3, 1, 1)

        b_ok = Gtk.Button(label="✓")
        b_ok.set_size_request(64, 48)
        b_ok.add_css_class("suggested-action")
        b_ok.add_css_class("keypad-button-ok")
        b_ok.connect("clicked", lambda _: self._submit_keypad())
        kp_grid.attach(b_ok, 2, 3, 1, 1)

        keypad_box.append(kp_grid)
        self.input_stack.add_named(keypad_box, "keypad")

        self.play_box.append(self.input_stack)
        self.stack.add_named(self.play_box, "playing")

        # 3. Écran des résultats
        self.res_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.res_box.set_valign(Gtk.Align.CENTER)
        self.res_box.set_halign(Gtk.Align.CENTER)

        self.res_icon = Gtk.Label(label="🎉")
        self.res_icon.add_css_class("chrono-icon")
        self.res_box.append(self.res_icon)

        self.res_title = Gtk.Label(label=_("chrono_finished"))
        self.res_title.add_css_class("title-1")
        self.res_box.append(self.res_title)

        self.res_score = Gtk.Label(label="")
        self.res_score.add_css_class("title-3")
        self.res_box.append(self.res_score)

        self.res_record = Gtk.Label(label="")
        self.res_record.add_css_class("heading")
        self.res_record.add_css_class("accent")
        self.res_box.append(self.res_record)

        r_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        r_btns.set_halign(Gtk.Align.CENTER)

        self.btn_res_again = Gtk.Button(label=_("btn_play_again"))
        self.btn_res_again.add_css_class("pill")
        self.btn_res_again.add_css_class("suggested-action")
        self.btn_res_again.connect("clicked", lambda _: self._on_start_chrono(None))
        r_btns.append(self.btn_res_again)

        self.btn_res_back = Gtk.Button(label=_("btn_back"))
        self.btn_res_back.add_css_class("pill")
        self.btn_res_back.connect("clicked", lambda _: self.reset_to_intro())
        r_btns.append(self.btn_res_back)

        self.res_box.append(r_btns)
        self.stack.add_named(self.res_box, "results")

        self.append(self.stack)
        self.reset_to_intro()

    def reset_to_intro(self):
        self._stop_timer()
        profile = StorageManager.get_instance().get_active_profile()
        self.best_label.set_label(_("best_score") + f" : {profile.chrono_best} pts")
        self.stack.set_visible_child_name("intro")

    def _on_start_chrono(self, btn):
        self.time_left = 60
        self.score = 0
        self.input_mode = "qcm" if self.btn_qcm_choice.get_active() else "keypad"
        self.input_stack.set_visible_child_name(self.input_mode)
        self.pad_display.set_visible(self.input_mode == "keypad")

        self.score_label.set_label(_("score") + " : 0")
        self.time_label.set_label(f"⏱️ {self.time_left}s")
        self.time_progress.set_fraction(1.0)

        self.stack.set_visible_child_name("playing")
        self._next_question()

        self._stop_timer()
        self.timer_source_id = GLib.timeout_add_seconds(1, self._on_timer_tick)

    def _stop_timer(self):
        if self.timer_source_id:
            GLib.source_remove(self.timer_source_id)
            self.timer_source_id = None

    def _on_timer_tick(self):
        self.time_left -= 1
        self.time_label.set_label(f"⏱️ {self.time_left}s")
        self.time_progress.set_fraction(self.time_left / 60.0)

        if self.time_left <= 0:
            self._end_chrono()
            return False
        return True

    def _abort_chrono(self, btn):
        self._stop_timer()
        self.reset_to_intro()

    def _next_question(self):
        # Tables 2 à 10 pour le chrono
        t = random.randint(2, 10)
        m = random.randint(2, 10)
        self.current_question = Question(t, m, "direct")

        self.q_label.set_label(self.current_question.display_text)
        self.user_input_buffer = ""
        self.pad_display.set_label("_")

        if self.input_mode == "qcm":
            self.qcm_options = self.current_question.generate_options()
            for i, opt in enumerate(self.qcm_options):
                btn = self.qcm_buttons[i]
                btn.set_label(str(opt))
                try:
                    btn.disconnect_by_func(self._on_qcm_click)
                except Exception:
                    pass

                def make_handler(val):
                    return lambda _: self._check_answer(val)

                btn.connect("clicked", make_handler(opt))

    def _append_digit(self, digit: str):
        if len(self.user_input_buffer) < 4:
            self.user_input_buffer += digit
            self.pad_display.set_label(self.user_input_buffer)

    def _clear_input(self):
        self.user_input_buffer = ""
        self.pad_display.set_label("_")

    def _submit_keypad(self):
        if not self.user_input_buffer:
            return
        try:
            val = int(self.user_input_buffer)
            self._check_answer(val)
        except ValueError:
            pass

    def _check_answer(self, user_val: int):
        if not self.current_question:
            return

        is_correct = (user_val == self.current_question.correct_answer)
        profile = StorageManager.get_instance().get_active_profile()
        profile.record_answer(self.current_question.table, is_correct)

        if is_correct:
            self.score += 1
            self.score_label.set_label(_("score") + f" : {self.score}")
            SoundManager.get_instance().play_success()
        else:
            SoundManager.get_instance().play_error()

        self._next_question()

    def _end_chrono(self):
        self._stop_timer()
        SoundManager.get_instance().play_level_complete()

        profile = StorageManager.get_instance().get_active_profile()
        is_record = profile.record_chrono(self.score)
        StorageManager.get_instance().save()

        self.res_score.set_label(_("chrono_result", score=self.score))
        if is_record:
            self.res_record.set_label(_("chrono_new_record"))
            self.res_record.set_visible(True)
        else:
            self.res_record.set_visible(False)

        self.stack.set_visible_child_name("results")

    def update_i18n(self):
        self.intro_title.set_label(_("chrono_title"))
        self.intro_desc.set_label(_("chrono_desc"))
        self.btn_start.set_label(_("chrono_start_btn"))
        self.btn_qcm_choice.set_label(_("dojo_mode_qcm"))
        self.btn_pad_choice.set_label(_("dojo_mode_keypad"))
        profile = StorageManager.get_instance().get_active_profile()
        self.best_label.set_label(_("best_score") + f" : {profile.chrono_best} pts")
