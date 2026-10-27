# 🌟 Multipli — Le jeu des tables de multiplication

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI Tests](https://github.com/smilebob/multipli/actions/workflows/ci.yml/badge.svg)](https://github.com/smilebob/multipli/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/smilebob/multipli/releases)
[![Platform](https://img.shields.io/badge/platform-Linux%20|%20macOS-lightgrey.svg)](#téléchargements--paquets)

**Multipli** est une application éducative **native GNOME** (GTK 4 & Libadwaita), conçue avec soin pour accompagner les élèves du **CE1 au CM2** dans l'apprentissage, la consolidation et la maîtrise complète des tables de multiplication (de 1 à 12).

![Multipli Banner](data/icons/org.gnome.Multipli.svg)

---

## 🎯 Conçu pour les élèves de l'école primaire

| Niveau | Tables ciblées | Mode d'interaction & Pédagogie |
| :--- | :--- | :--- |
| **🌱 CE1** | **2, 5 et 10** | Démarrage en douceur avec grands boutons **QCM (4 choix)**, encouragements chaleureux. |
| **🌿 CE2** | **3, 4, 5, 6** | Consolidation des tables fondamentales, choix QCM ou Pavé numérique. |
| **⚡ CM1** | **6, 7, 8, 9** | Perfectionnement, introduction des **facteurs à trous** (ex: $6 \times ? = 42$), pavé tactile & clavier direct. |
| **👑 CM2** | **Toutes (2 à 12)** | Défi Grand Maître : mélanges aléatoires, calcul mental rapide et facteurs manquants. |

---

## 🎮 Les 5 Modes de jeu intégrés

1. 🗺️ **Mode Aventure par classe** :
   - Progression étape par étape (CE1 $\rightarrow$ CE2 $\rightarrow$ CM1 $\rightarrow$ CM2).
   - Décroche jusqu'à 3 étoiles (⭐ ⭐ ⭐) par niveau.
   - Les niveaux se débloquent au fil des réussites.
2. 🥋 **Le Dojo d'Entraînement** :
   - Choisis librement les tables à réviser sans pression de temps.
   - Choix entre saisie par QCM ou saisie libre au pavé numérique.
3. ⏱️ **Le Défi Chrono 60s** :
   - 60 secondes pour battre ton record personnel de bonnes réponses !
4. 📐 **Table de Pythagore Interactive** :
   - Explore les tables de 1 à 10, visualise les motifs géométriques et la commutativité.
   - Carte de chaleur indiquant la maîtrise de chaque multiplication.
5. 👤 **Gestion Multi-Profils** :
   - Créez un profil pour chaque enfant avec avatar, prénom et niveau de départ personnalisable.
   - Édition et historique individuel des réussites.

---

## 📦 Téléchargements & Paquets

Les paquets pré-compilés sont disponibles directement dans les [Releases GitHub](https://github.com/smilebob/multipli/releases) :

- **Debian / Ubuntu (`.deb`)** :
  - `multipli_1.0.0_amd64.deb` (Intel / AMD 64 bits)
  - `multipli_1.0.0_arm64.deb` (ARM 64 bits / Raspberry Pi)
  ```bash
  sudo apt install ./multipli_1.0.0_amd64.deb
  ```
- **Flatpak (Linux multi-distributions)** :
  - `org.gnome.Multipli.flatpak`
  ```bash
  flatpak install org.gnome.Multipli.flatpak
  ```
- **macOS (`.dmg`)** :
  - `Multipli-1.0.0-arm64.dmg` (Apple Silicon M1/M2/M3/M4)
  - `Multipli-1.0.0-x86_64.dmg` (Intel Mac)

---

## 🚀 Lancement & Installation locale

### Lancement direct :
```bash
python3 main.py
```

### Installation système via script :
```bash
./install.sh
```

---

## 📚 Documentation

- 📖 [Guide Utilisateur complet (Français)](docs/GUIDE_UTILISATEUR.md)
- 📖 [User Guide (English)](docs/USER_GUIDE.md)
- 🛠️ [Guide Développeur (Architecture, Packaging, i18n)](docs/DEVELOPMENT.md)
- 🤖 [Instructions pour Agents IA (AGENTS.md)](AGENTS.md)

---

## ⚖️ Licence

Ce projet est distribué sous licence libre **Apache 2.0**. Consultez le fichier [LICENSE](LICENSE) pour plus de détails.
Des informations sur la licence et le dépôt open-source sont également directement consultables dans l'application via le dialogue *Préférences* et *À propos de Multipli*.
