"""
Vue active d'un exercice / partie de calcul.
Prend en charge le mode QCM (4 grands boutons) et le mode Pavé numérique / Clavier physique direct.
"""

import random
from typing import Callable, List, Optional
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gdk

from multipli.i18n import _
from multipli.audio import SoundManager
from multipli.models import StorageManager


class Question:
    def __init__(self, table: int, multiplier: int, q_type: str = "direct"):
        self.table = table
        self.multiplier = multiplier
        self.result = table * multiplier
        self.q_type = q_type  # "direct", "missing_factor_a", "missing_factor_b"

        if q_type == "direct":
            self.display_text = f"{table} × {multiplier} = ?"
            self.correct_answer = self.result
            self.full_equation = f"{table} × {multiplier} = {self.result}"
        elif q_type == "missing_factor_a":
            self.display_text = f"? × {multiplier} = {self.result}"
            self.correct_answer = table
            self.full_equation = f"{table} × {multiplier} = {self.result}"
        else:  # "missing_factor_b"
            self.display_text = f"{table} × ? = {self.result}"
            self.correct_answer = multiplier
            self.full_equation = f"{table} × {multiplier} = {self.result}"

    def generate_options(self) -> List[int]:
        correct = self.correct_answer
        options = {correct}

        # Générer des distracteurs plausibles et proches
        if self.q_type == "direct":
            candidates = [
                correct + self.table,
                correct - self.table,
                correct + self.multiplier,
                correct - self.multiplier,
                correct + random.choice([-2, -1, 1, 2]),
                (self.table + 1) * self.multiplier,
                (self.table - 1) * self.multiplier,
            ]
        else:
            candidates = [
                correct + 1,
                correct - 1,
                correct + 2,
                correct - 2,
                random.randint(1, 10),
            ]

        for cand in candidates:
            if cand > 0 and cand != correct:
                options.add(cand)
            if len(options) >= 4:
                break

        while len(options) < 4:
            cand = max(1, correct + random.randint(-5, 5))
            if cand > 0:
                options.add(cand)

        res = list(options)[:4]
        random.shuffle(res)
        return res


class GameView(Gtk.Box):
    def __init__(self, on_back_callback: Callable[[], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.on_back_callback = on_back_callback

        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)

        self.questions: List[Question] = []
        self.current_idx = 0
        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.input_mode = "qcm"  # "qcm" ou "keypad"
        self.user_input_buffer = ""
        self.is_answered = False
        self.level_id: Optional[str] = None  # Si partie en mode aventure

        self._build_ui()
        self._setup_keyboard_events()

    def _setup_keyboard_events(self):
        controller = Gtk.EventControllerKey.new()
        controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        controller.connect("key-pressed", lambda c, k, kc, s: self.handle_key(k))
        self.add_controller(controller)

    def handle_key(self, keyval: int) -> bool:
        ENTER_KEYS = (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_ISO_Enter)

        if self.is_answered:
            # Si déjà répondu, Entrée ou Espace passe immédiatement à la suite
            if keyval in ENTER_KEYS or keyval == Gdk.KEY_space:
                self._next_question()
                return True
            return False

        if self.input_mode == "qcm":
            # Touches 1, 2, 3, 4 pour choisir une réponse QCM
            qcm_keys = {
                Gdk.KEY_1: 0, Gdk.KEY_KP_1: 0, Gdk.KEY_ampersand: 0,
                Gdk.KEY_2: 1, Gdk.KEY_KP_2: 1, Gdk.KEY_eacute: 1,
                Gdk.KEY_3: 2, Gdk.KEY_KP_3: 2, Gdk.KEY_quotedbl: 2,
                Gdk.KEY_4: 3, Gdk.KEY_KP_4: 3, Gdk.KEY_apostrophe: 3,
            }
            if keyval in qcm_keys:
                idx = qcm_keys[keyval]
                if idx < len(self.qcm_options):
                    self._on_qcm_button_clicked(idx)
                    return True
        else:
            # Mode Pavé numérique / saisie clavier direct
            # 1. Validation immédiate avec la touche Entrée (clavier principal ou pavé numérique)
            if keyval in ENTER_KEYS:
                self._submit_keypad_answer()
                return True

            # 2. Effacement d'un chiffre avec Retour arrière ou Suppr
            if keyval in (Gdk.KEY_BackSpace, Gdk.KEY_Delete):
                self._backspace_input()
                return True

            # 3. Chiffres AZERTY (rangée supérieure non shiftée)
            azerty_digits = {
                Gdk.KEY_agrave: "0",
                Gdk.KEY_ampersand: "1",
                Gdk.KEY_eacute: "2",
                Gdk.KEY_quotedbl: "3",
                Gdk.KEY_apostrophe: "4",
                Gdk.KEY_parenleft: "5",
                Gdk.KEY_minus: "6",
                Gdk.KEY_egrave: "7",
                Gdk.KEY_underscore: "8",
                Gdk.KEY_ccedilla: "9",
            }
            if keyval in azerty_digits:
                self._append_digit(azerty_digits[keyval])
                return True

            # 4. Pavé numérique physique (KP_0 .. KP_9)
            kp_digits = {
                Gdk.KEY_KP_0: "0", Gdk.KEY_KP_1: "1", Gdk.KEY_KP_2: "2",
                Gdk.KEY_KP_3: "3", Gdk.KEY_KP_4: "4", Gdk.KEY_KP_5: "5",
                Gdk.KEY_KP_6: "6", Gdk.KEY_KP_7: "7", Gdk.KEY_KP_8: "8",
                Gdk.KEY_KP_9: "9",
            }
            if keyval in kp_digits:
                self._append_digit(kp_digits[keyval])
                return True

            # 5. Conversion universelle de caractère numérique unicode (QWERTY, etc.)
            char_code = Gdk.keyval_to_unicode(keyval)
            if char_code:
                try:
                    char_str = chr(char_code)
                    if char_str.isdigit():
                        self._append_digit(char_str)
                        return True
                except Exception:
                    pass

        return False

    def _build_ui(self):
        # Barre d'état en haut
        top_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        top_bar.set_hexpand(True)

        self.btn_back = Gtk.Button(label=_("btn_back"))
        self.btn_back.add_css_class("flat")
        self.btn_back.connect("clicked", lambda b: self.on_back_callback())
        top_bar.append(self.btn_back)

        self.progress_label = Gtk.Label(label="")
        self.progress_label.set_hexpand(True)
        self.progress_label.set_halign(Gtk.Align.CENTER)
        self.progress_label.add_css_class("title-4")
        top_bar.append(self.progress_label)

        self.streak_label = Gtk.Label(label="🔥 0")
        self.streak_label.add_css_class("heading")
        self.streak_label.add_css_class("accent")
        top_bar.append(self.streak_label)

        self.append(top_bar)

        # Barre de progression visuelle
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_fraction(0.0)
        self.append(self.progress_bar)

        # Zone centrale déroulante et restreinte avec Adw.Clamp
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        clamp = Adw.Clamp()
        clamp.set_maximum_size(600)
        clamp.set_tightening_threshold(520)

        self.play_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.play_container.set_valign(Gtk.Align.CENTER)
        self.play_container.set_margin_top(8)
        self.play_container.set_margin_bottom(12)
        self.play_container.set_margin_start(16)
        self.play_container.set_margin_end(16)

        # Carte centrale du calcul
        calc_card = Adw.Bin()
        calc_card.add_css_class("card")
        calc_card.set_hexpand(True)

        calc_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        calc_box.set_margin_top(16)
        calc_box.set_margin_bottom(16)
        calc_box.set_margin_start(16)
        calc_box.set_margin_end(16)
        calc_box.set_halign(Gtk.Align.CENTER)

        self.question_label = Gtk.Label(label="7 × 8 = ?")
        self.question_label.add_css_class("calc-question")
        calc_box.append(self.question_label)

        # Zone d'affichage de la saisie utilisateur (mode pavé)
        self.input_display_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.input_display_box.set_halign(Gtk.Align.CENTER)
        self.input_display_label = Gtk.Label(label="_")
        self.input_display_label.add_css_class("calc-input-display")
        self.input_display_box.append(self.input_display_label)
        calc_box.append(self.input_display_box)

        # Zone de feedback / félicitations / explication
        self.feedback_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.feedback_box.set_halign(Gtk.Align.CENTER)

        self.feedback_label = Gtk.Label(label="")
        self.feedback_label.add_css_class("title-3")
        self.feedback_sub = Gtk.Label(label="")
        self.feedback_sub.add_css_class("body")

        self.feedback_box.append(self.feedback_label)
        self.feedback_box.append(self.feedback_sub)
        calc_box.append(self.feedback_box)

        calc_card.set_child(calc_box)
        self.play_container.append(calc_card)

        # Zone des contrôles de saisie (QCM ou Pavé)
        self.input_stack = Gtk.Stack()
        self.input_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        # 1. Mode QCM
        self.qcm_box = Gtk.Grid()
        self.qcm_box.set_row_spacing(10)
        self.qcm_box.set_column_spacing(10)
        self.qcm_box.set_halign(Gtk.Align.CENTER)

        self.qcm_buttons = []
        self.qcm_options = []
        for i in range(4):
            btn = Gtk.Button(label="--")
            btn.set_size_request(130, 52)
            btn.add_css_class("qcm-button")
            btn.set_focusable(False)
            row = i // 2
            col = i % 2
            self.qcm_box.attach(btn, col, row, 1, 1)
            # Connexion unique et pérenne du signal de clic
            btn.connect("clicked", lambda _, idx=i: self._on_qcm_button_clicked(idx))
            self.qcm_buttons.append(btn)

        self.input_stack.add_named(self.qcm_box, "qcm")

        # 2. Mode Pavé numérique
        self.keypad_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.keypad_box.set_halign(Gtk.Align.CENTER)

        grid_pad = Gtk.Grid()
        grid_pad.set_row_spacing(6)
        grid_pad.set_column_spacing(6)

        # Boutons 1 à 9
        for num in range(1, 10):
            r = (num - 1) // 3
            c = (num - 1) % 3
            b = Gtk.Button(label=str(num))
            b.set_size_request(66, 50)
            b.add_css_class("keypad-button")
            b.set_focusable(False)
            digit = str(num)
            b.connect("clicked", lambda _, d=digit: self._append_digit(d))
            grid_pad.attach(b, c, r, 1, 1)

        # Ligne du bas : Effacer (C), 0, Valider (✓)
        btn_c = Gtk.Button(label="⌫")
        btn_c.set_size_request(66, 50)
        btn_c.add_css_class("keypad-button-clear")
        btn_c.set_focusable(False)
        btn_c.connect("clicked", lambda _: self._backspace_input())
        grid_pad.attach(btn_c, 0, 3, 1, 1)

        btn_0 = Gtk.Button(label="0")
        btn_0.set_size_request(66, 50)
        btn_0.add_css_class("keypad-button")
        btn_0.set_focusable(False)
        btn_0.connect("clicked", lambda _: self._append_digit("0"))
        grid_pad.attach(btn_0, 1, 3, 1, 1)

        btn_ok = Gtk.Button(label="✓")
        btn_ok.set_size_request(66, 50)
        btn_ok.add_css_class("suggested-action")
        btn_ok.add_css_class("keypad-button-ok")
        btn_ok.set_focusable(False)
        btn_ok.connect("clicked", lambda _: self._submit_keypad_answer())
        grid_pad.attach(btn_ok, 2, 3, 1, 1)

        self.keypad_box.append(grid_pad)
        self.input_stack.add_named(self.keypad_box, "keypad")

        self.play_container.append(self.input_stack)

        # Bouton Suivant (s'active après réponse si besoin)
        self.btn_next = Gtk.Button(label=_("btn_next"))
        self.btn_next.set_halign(Gtk.Align.CENTER)
        self.btn_next.add_css_class("pill")
        self.btn_next.add_css_class("suggested-action")
        self.btn_next.connect("clicked", lambda b: self._next_question())
        self.btn_next.set_visible(False)
        self.play_container.append(self.btn_next)

        # Boutons d'action pour la fin de partie (réutilisables sans duplication)
        self.results_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self.results_btn_box.set_halign(Gtk.Align.CENTER)
        self.results_btn_box.set_margin_top(16)
        self.results_btn_box.set_visible(False)

        self.btn_retry = Gtk.Button(label=_("btn_play_again"))
        self.btn_retry.add_css_class("pill")
        self.btn_retry.add_css_class("suggested-action")
        self.btn_retry.connect("clicked", self._on_retry_clicked)
        self.results_btn_box.append(self.btn_retry)

        self.btn_menu = Gtk.Button(label=_("btn_back"))
        self.btn_menu.add_css_class("pill")
        self.btn_menu.connect("clicked", lambda _: self.on_back_callback())
        self.results_btn_box.append(self.btn_menu)

        self.play_container.append(self.results_btn_box)

        clamp.set_child(self.play_container)
        scroll.set_child(clamp)
        self.append(scroll)

    def start_game(
        self,
        tables: List[int],
        total_questions: int = 10,
        input_mode: str = "qcm",
        question_types: List[str] = None,
        level_id: Optional[str] = None,
    ):
        self.tables = list(tables)
        self.total_questions = total_questions
        self.input_mode = input_mode
        self.question_types = list(question_types) if question_types else ["direct"]
        self.level_id = level_id
        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.current_idx = 0
        self.user_input_buffer = ""
        self.is_answered = False

        # Générer la liste des questions
        self.questions = []
        for _ in range(total_questions):
            t = random.choice(self.tables)
            m = random.randint(1, 10)
            q_type = random.choice(self.question_types)
            self.questions.append(Question(t, m, q_type))

        self.input_stack.set_visible(True)
        self.input_stack.set_visible_child_name(self.input_mode)
        self.input_display_box.set_visible(self.input_mode == "keypad")
        self.results_btn_box.set_visible(False)

        self._show_question()

    def _show_question(self):
        if self.current_idx >= len(self.questions):
            self._show_results()
            return

        self.is_answered = False
        q = self.questions[self.current_idx]

        # Mettre à jour l'en-tête
        self.progress_label.set_label(
            _("question_progress", current=self.current_idx + 1, total=len(self.questions))
        )
        fraction = self.current_idx / len(self.questions)
        self.progress_bar.set_fraction(fraction)
        self.streak_label.set_label(f"🔥 {self.streak}")

        # Texte du calcul
        self.question_label.set_label(q.display_text)
        self.user_input_buffer = ""
        self.input_display_label.set_label("_")

        # Cacher feedback et bouton suivant
        self.feedback_box.set_visible(False)
        self.btn_next.set_visible(False)
        self.results_btn_box.set_visible(False)

        # Assurer la visibilité du mode de saisie
        self.input_stack.set_visible(True)
        self.input_stack.set_visible_child_name(self.input_mode)
        self.input_display_box.set_visible(self.input_mode == "keypad")

        # Préparer le mode d'entrée
        if self.input_mode == "qcm":
            self.qcm_box.set_visible(True)
            self.qcm_options = q.generate_options()
            for i, opt in enumerate(self.qcm_options):
                btn = self.qcm_buttons[i]
                btn.set_label(str(opt))
                btn.set_sensitive(True)
                btn.remove_css_class("qcm-correct")
                btn.remove_css_class("qcm-wrong")

    def _on_qcm_button_clicked(self, index: int):
        if not self.is_answered and 0 <= index < len(self.qcm_options):
            self._check_answer(self.qcm_options[index], self.qcm_buttons[index])

    def _append_digit(self, digit: str):
        if self.is_answered:
            return
        if len(self.user_input_buffer) < 4:
            self.user_input_buffer += digit
            self.input_display_label.set_label(self.user_input_buffer)

    def _backspace_input(self):
        if self.is_answered:
            return
        if self.user_input_buffer:
            self.user_input_buffer = self.user_input_buffer[:-1]
            self.input_display_label.set_label(self.user_input_buffer if self.user_input_buffer else "_")

    def _clear_input(self):
        if self.is_answered:
            return
        self.user_input_buffer = ""
        self.input_display_label.set_label("_")

    def _submit_keypad_answer(self):
        if self.is_answered or not self.user_input_buffer:
            return
        try:
            val = int(self.user_input_buffer)
            self._check_answer(val, None)
        except ValueError:
            pass

    def _check_answer(self, user_val: int, clicked_btn: Optional[Gtk.Button]):
        if self.is_answered:
            return
        self.is_answered = True

        q = self.questions[self.current_idx]
        is_correct = (user_val == q.correct_answer)
        profile = StorageManager.get_instance().get_active_profile()

        # Enregistrer les statistiques pour la table travaillée
        profile.record_answer(q.table, is_correct)

        if is_correct:
            self.score += 1
            self.streak += 1
            if self.streak > self.max_streak:
                self.max_streak = self.streak
            profile.record_streak(self.streak)
            SoundManager.get_instance().play_success()

            self.feedback_label.set_label(random.choice([_("feedback_perfect"), _("feedback_great"), _("feedback_bravo")]))
            self.feedback_label.remove_css_class("feedback-error")
            self.feedback_label.add_css_class("feedback-success")
            self.feedback_sub.set_label(f"✓ {q.full_equation}")

            if clicked_btn:
                clicked_btn.add_css_class("qcm-correct")

            # Passage automatique rapide à la question suivante après 850 ms
            self.feedback_box.set_visible(True)
            GLib.timeout_add(850, self._auto_advance)

        else:
            self.streak = 0
            SoundManager.get_instance().play_error()

            self.feedback_label.set_label(_("feedback_oops"))
            self.feedback_label.remove_css_class("feedback-success")
            self.feedback_label.add_css_class("feedback-error")
            self.feedback_sub.set_label(_("feedback_correct_answer", ans=q.full_equation))

            if clicked_btn:
                clicked_btn.add_css_class("qcm-wrong")

            # En cas d'erreur, laisser l'enfant lire la bonne réponse et cliquer sur "Suivant"
            self.feedback_box.set_visible(True)
            self.btn_next.set_visible(True)

        self.streak_label.set_label(f"🔥 {self.streak}")
        StorageManager.get_instance().save()

    def _auto_advance(self):
        if self.is_answered and self.feedback_label.has_css_class("feedback-success"):
            self._next_question()
        return False

    def _next_question(self):
        self.current_idx += 1
        self._show_question()

    def _show_results(self):
        # Fin de la session : calcul des étoiles et écran récapitulatif
        total = len(self.questions)
        ratio = (self.score / total) if total > 0 else 0
        stars = 3 if ratio >= 0.9 else (2 if ratio >= 0.7 else (1 if ratio >= 0.5 else 0))

        profile = StorageManager.get_instance().get_active_profile()
        if self.level_id:
            profile.update_level_stars(self.level_id, stars)
            StorageManager.get_instance().save()

        if stars >= 2:
            SoundManager.get_instance().play_level_complete()

        # Nettoyage de la vue pour afficher les résultats
        self.progress_bar.set_fraction(1.0)
        self.input_stack.set_visible(False)
        self.btn_next.set_visible(False)
        self.input_display_box.set_visible(False)

        stars_str = "⭐" * stars if stars > 0 else "💪"
        self.question_label.set_label(stars_str)

        self.feedback_box.set_visible(True)
        self.feedback_label.remove_css_class("feedback-error")
        self.feedback_label.add_css_class("feedback-success")
        self.feedback_label.set_label(_("level_completed") if stars >= 2 else _("score") + f" : {self.score}/{total}")
        self.feedback_sub.set_label(f"{self.score} / {total} bonnes réponses • Meilleure série : {self.max_streak}")
        self.results_btn_box.set_visible(True)

    def _on_retry_clicked(self, btn):
        self.start_game(
            self.tables,
            self.total_questions,
            self.input_mode,
            self.question_types,
            self.level_id
        )
