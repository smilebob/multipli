# 🌟 Multipli — Le jeu des tables de multiplication

**Multipli** est une application éducative **native GNOME** (GTK 4 & Libadwaita), conçue avec soin pour accompagner les élèves du **CE1 au CM2** dans l'apprentissage, la consolidation et la maîtrise complète des tables de multiplication (de 1 à 12).

![Icon](data/icons/org.gnome.Multipli.svg)

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

2. 🥋 **Le Dojo libre (Entraînement sur-mesure)** :
   - Choix libre des tables à travailler (sélection multiple parmi 1 à 12).
   - Choix du type de calcul : Direct ($7 \times 8 = ?$), Facteur manquant ($7 \times ? = 56$), ou Mélange.
   - Choix du nombre de questions (10, 15, 20) et du mode de réponse (QCM ou Pavé numérique).

3. ⏱️ **Course contre la montre (Chrono 60s)** :
   - 60 secondes pour résoudre un maximum de calculs !
   - Enregistrement du record personnel pour stimuler la motivation.

4. 📐 **Table de Pythagore interactive** :
   - Grille complète et visuelle de $10 \times 10$ ou $12 \times 12$.
   - Met en lumière la commutativité magique ($a \times b = b \times a$) et les nombres carrés ($a \times a$).
   - Idéal pour réviser avant de commencer à jouer.

5. 🏆 **Mes Progrès & Mes Trophées** :
   - Suivi précis de la maîtrise de **chaque table** avec pourcentage de réussite pour repérer immédiatement les tables à retravailler (badge *"À réviser !"* ou *"Parfait !*").
   - Galerie de trophées à collectionner (*Premier Pas*, *En Feu !*, *Éclair*, *Diplômé CE1*, *Génie des Tables*).

---

## 👥 Multi-profils (pour toute la fratrie)

- Créez facilement un profil pour chaque enfant avec un prénom et un avatar rigolo (🦊, 🐼, 🦉, 🐱, 🦁, 🦄, 🚀, ⭐).
- Chaque profil conserve ses propres étoiles, ses records chronométrés et ses statistiques par table.
- Changement de joueur en 1 clic depuis le bouton en haut à gauche.

---

## 🌐 Système multilingue modulaire & ultra-facile à enrichir

Multipli est livré avec **4 langues prêtes à l'emploi** :
- 🇫🇷 **Français** (`locales/fr.json`)
- 🇬🇧 **English** (`locales/en.json`)
- 🇪🇸 **Español** (`locales/es.json`)
- 🇩🇪 **Deutsch** (`locales/de.json`)

Le changement de langue se fait instantanément depuis le menu **Préférences** (`Ctrl+,`).

### ➕ Comment ajouter une nouvelle langue en 2 minutes ?
Aucune compilation ni outil complexe n'est requis :
1. Allez dans le dossier `locales/`.
2. Dupliquez `en.json` (ou `fr.json`) et renommez-le, par exemple `it.json` pour l'italien ou `pt.json` pour le portugais.
3. Renseignez `"lang_name"` (ex: `"Italiano"`) et `"lang_flag"` (ex: `"🇮🇹"`), puis traduisez les textes.
4. **C'est tout !** Multipli détecte automatiquement le nouveau fichier au démarrage ou via le menu des Préférences.

---

## ⌨️ Raccourcis clavier & Contrôles

- **Touches 1, 2, 3, 4** : Sélection directe des options QCM.
- **Pavé numérique / Chiffres 0 à 9** : Saisie instantanée des nombres.
- **Touche Entrée / Espace** : Valider la réponse ou passer à la question suivante.
- **Touche Retour arrière** : Effacer la saisie.
- **Ctrl + Q** : Quitter l'application.
- **Ctrl + ,** : Ouvrir les Préférences.

---

## 🚀 Lancement & Installation

### Lancement direct (sans installation) :
```bash
./multipli
```

### Installation dans le système GNOME :
Pour intégrer Multipli dans votre lanceur d'applications GNOME avec son icône officielle :
```bash
./install.sh
```
L'application apparaîtra dans votre menu d'applications GNOME et pourra être lancée via la commande `multipli`.

### Désinstallation propre :
```bash
./install.sh --uninstall
```

---

## 🛠️ Dépendances système requises

L'application utilise l'écosystème natif GNOME standard sous Linux :
- `python3`
- `python3-gi` (PyGObject)
- `gir1.2-gtk-4.0`
- `gir1.2-adw-1` (Libadwaita)
- `gir1.2-gstreamer-1.0` (pour la synthèse des carillons et sons de succès)

Sous Ubuntu/Debian/Fedora, ces composants sont généralement déjà installés avec GNOME ou s'installent via :
```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-gstreamer-1.0
```
