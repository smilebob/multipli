# Developer Documentation — Multipli

Welcome to the **Multipli** developer guide! This document explains how to set up the development environment, understand the software architecture, run tests, and package the application across supported platforms.

---

## 1. Project Architecture

Multipli is built with **Python 3.10+**, **GTK4**, and **Libadwaita** (`libadwaita-1`), following GNOME Human Interface Guidelines (HIG).

```
multipli/
├── data/
│   ├── icons/                          # Application SVGs & symbolic icons
│   ├── org.gnome.Multipli.desktop      # Desktop entry
│   └── org.gnome.Multipli.metainfo.xml # AppStream metadata for Flathub / GNOME Software
├── locales/                            # Internationalization JSON dictionaries
│   ├── fr.json
│   ├── en.json
│   ├── es.json
│   └── de.json
├── multipli/                           # Core application package
│   ├── __init__.py
│   ├── adventure_view.py               # World / level progression map
│   ├── audio_manager.py                # GStreamer / sound effects player
│   ├── dojo_view.py                    # Free training mode
│   ├── game_view.py                    # Gameplay screen (QCM & Keypad + animations)
│   ├── i18n.py                         # Reactive localization engine
│   ├── preferences_dialog.py           # Adw.PreferencesDialog (settings & license)
│   ├── profile_manager.py              # SQLite / JSON profile persistence
│   ├── pythagoras_view.py              # Interactive Pythagoras matrix
│   ├── speedrun_view.py                # 60s Chrono challenge
│   └── window.py                       # Adw.ApplicationWindow & event controllers
├── packaging/
│   ├── deb/                            # Debian / Ubuntu .deb build scripts
│   ├── flatpak/                        # GNOME Flatpak manifest
│   └── macos/                          # macOS .app bundle & .dmg build scripts
├── tests/                              # Unittest automated test suite
├── main.py                             # Adw.Application entry point
├── pyproject.toml                      # Standard PEP 517/621 packaging metadata
└── LICENSE                             # Apache 2.0 License
```

---

## 2. Setting Up the Development Environment

### Prerequisites on Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-gi \
    gir1.2-gtk-4.0 \
    gir1.2-adw-1 \
    gir1.2-gstreamer-1.0 \
    gstreamer1.0-plugins-good \
    xvfb
```

### Running the Application Locally

```bash
python3 main.py
```

---

## 3. Automated Testing

Multipli includes an automated `unittest` test suite covering business logic, i18n, profiles, and GTK widget behavior.

To run the entire test suite locally:
```bash
python3 -m unittest discover -s tests -v
```

In headless or CI environments without a display:
```bash
xvfb-run -a python3 -m unittest discover -s tests -v
```

---

## 4. Internationalization (i18n)

The application uses dynamic JSON translation tables managed by [`multipli.i18n.I18nManager`](file:///home/pierre/Documents/antigravity/delightful-bose/multipli/i18n.py).

### Adding a New Language:
1. Create `locales/<lang_code>.json` (copy `locales/en.json` as a baseline).
2. Register `<lang_code>` in [`multipli/i18n.py`](file:///home/pierre/Documents/antigravity/delightful-bose/multipli/i18n.py) in `SUPPORTED_LANGUAGES`.
3. Add the language entry to the `PreferencesDialog` language dropdown.

Translations support format placeholders (e.g., `{count}`, `{name}`).

---

## 5. Keyboard Handling in GTK4

GTK4 handles focus strictly. To capture global shortcuts (such as `Return`, `KP_Enter`, number keys) without needing a focused text entry:
- An `EventControllerKey` is attached to `MultipliWindow` in phase `Gtk.PropagationPhase.CAPTURE`.
- Interactive keypad buttons set `set_focusable(False)` so mouse clicks do not intercept subsequent keyboard events.

---

## 6. Packaging & CI/CD

### Debian / Ubuntu `.deb`
Run:
```bash
bash packaging/deb/build_deb.sh 1.0.0 amd64
# Or for arm64:
bash packaging/deb/build_deb.sh 1.0.0 arm64
```
Generates `dist/multipli_1.0.0_<arch>.deb`.

### Flatpak
Manifest: `packaging/flatpak/org.gnome.Multipli.yml` targeting runtime `org.gnome.Platform//47`.
Run:
```bash
bash packaging/flatpak/build_flatpak.sh
```

### macOS `.dmg`
Builds a standalone `.app` bundle using embedded Python and packages it with `hdiutil`:
```bash
bash packaging/macos/build_dmg.sh 1.0.0 arm64
```

### GitHub Actions
The repository includes:
- `.github/workflows/ci.yml`: Runs tests on pull requests and commits to `main`.
- `.github/workflows/release.yml`: Triggered upon pushing a tag `v*.*.*`, compiles `.deb`, `.flatpak`, and `.dmg` binaries across architectures, and automatically publishes a GitHub Release.
