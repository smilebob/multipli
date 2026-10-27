# AI Agent Guidelines & Context — Multipli

This file provides architectural context, development constraints, and guidelines for AI Agents (Antigravity, Copilot, Claude Code, Cursor, etc.) working on the **Multipli** codebase.

---

## 1. Project Identity & Stack
- **App Name**: Multipli (`org.gnome.Multipli`)
- **Repository**: `https://github.com/smilebob/multipli`
- **Target Audience**: Elementary & middle school children (CE1 to CM2, ages 6–11) learning multiplication.
- **Licence**: Apache License 2.0 (Strictly enforced in code headers, About dialog, and settings).
- **Core Technology**: Python 3.10+, PyGObject (`gi.repository`), GTK4, Libadwaita (`Adw`), GStreamer (`Gst`).

---

## 2. Key Architectural Invariants

### 1. GNOME & Libadwaita Human Interface Guidelines (HIG)
- Use standard Adwaita widgets: `Adw.ToolbarView`, `Adw.HeaderBar`, `Adw.ViewStack`, `Adw.ViewSwitcherBar`, `Adw.PreferencesDialog`, `Adw.ActionRow`.
- Do NOT use deprecated GTK3 or obsolete GTK4 APIs (`Gtk.Stock`, `show_all()`, `set_can_focus` without proper type, etc.).
- Responsive sizing: Default window dimensions must accommodate smaller screens (`780x620` min / `860x680` default).
- Modals & Dialogs: Use `Adw.Dialog` or `Adw.PreferencesDialog` with explicit parent references (`dialog.present(parent_window)`).

### 2. State & Signal Management
- **Single Source of Truth**: User profile data, mastery scores, stars, and history are encapsulated within [`multipli.profile_manager.ProfileManager`](file:///home/pierre/Documents/antigravity/delightful-bose/multipli/profile_manager.py).
- **Signal Handlers & Closures**: NEVER connect event handlers (e.g. `button.connect("clicked", ...)`) inside repeated render loops like `_show_question()`! This creates memory leaks and triggers stale callbacks on subsequent iterations. Instead:
  - Connect signals once during `__init__`.
  - Pass indexes or read dynamically updated instance state.
- **View Stack Visibility**: When switching sub-views or resetting game screens, ensure child visibility is maintained: `self.input_stack.set_visible(True)`.

### 3. Keyboard Input & Propagation
- When gameplay views require physical keyboard interaction (keypad digits, `Return`, `KP_Enter`, `Backspace`), do not rely on focus inside child boxes.
- Route keyboard handling via `MultipliWindow` using an `EventControllerKey` installed in `Gtk.PropagationPhase.CAPTURE`.
- Set `set_focusable(False)` on interactive buttons (e.g., keypad buttons) so mouse clicks do not swallow future keyboard strokes.

### 4. Internationalization (i18n)
- Never hardcode user-facing strings in Python source files.
- Use `_("key_name")` via [`multipli.i18n.get_i18n().get_text`](file:///home/pierre/Documents/antigravity/delightful-bose/multipli/i18n.py).
- Ensure all supported languages (`locales/fr.json`, `locales/en.json`, `locales/es.json`, `locales/de.json`) contain the exact same keys.

---

## 3. Testing & Verification Requirements

Before submitting or committing any change:
1. Run the headless unit and integration test suite:
   ```bash
   xvfb-run -a python3 -m unittest discover -s tests -v
   ```
2. Verify that all 31+ test cases pass without regressions.
3. If new gameplay features or dialogs are added, write matching unit tests under `tests/test_*.py`.

---

## 4. Packaging & Release Conventions
- **Version Number**: SemVer format (`vMAJOR.MINOR.PATCH`). Managed in `pyproject.toml` and release tags.
- **Git Branching**: Main branch is `main`.
- **Packaging Scripts**: Stored in `packaging/deb/`, `packaging/flatpak/`, and `packaging/macos/`.
- **CI/CD**: Workflows in `.github/workflows/ci.yml` and `.github/workflows/release.yml`. Releases are published when a git tag `v*` is pushed.
