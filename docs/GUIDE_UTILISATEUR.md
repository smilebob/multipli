# Guide Utilisateur — Multipli

Bienvenue dans **Multipli**, l'application native GNOME conçue avec amour pour accompagner les enfants du **CE1 au CM2** (et au-delà !) dans l'apprentissage et la maîtrise ludique des tables de multiplication.

---

## Sommaire
1. [Installation et Lancement](#installation-et-lancement)
2. [Gestion des Profils](#gestion-des-profils)
3. [Les Modes de Jeu](#les-modes-de-jeu)
   - [Aventure Galactique](#1-laventure-galactique)
   - [Dojo d'Entraînement](#2-le-dojo-dentraînement)
   - [Chrono 60s](#3-le-chrono-60s)
   - [Table de Pythagore](#4-la-table-de-pythagore-interactive)
4. [Types de Saisie et Raccourcis Clavier](#types-de-saisie-et-raccourcis-clavier)
5. [Statistiques et Récompenses](#statistiques-et-récompenses)
6. [Personnalisation et Préférences](#personnalisation-et-préférences)

---

## Installation et Lancement

Multipli est disponible sous plusieurs formats :
- **Paquet Debian / Ubuntu (`.deb`)** : Double-cliquez sur le fichier téléchargé ou installez-le avec `sudo apt install ./multipli_1.0.0_amd64.deb`.
- **Flatpak (`.flatpak`)** : `flatpak install org.gnome.Multipli.flatpak`
- **macOS (`.dmg`)** : Ouvrez le fichier `.dmg` et glissez l'icône `Multipli.app` dans le dossier *Applications*.

Lancez l'application depuis votre lanceur d'applications sous GNOME ou tapez `multipli` dans un terminal.

---

## Gestion des Profils

Multipli permet à plusieurs enfants ou membres d'une même famille de jouer sur la même machine tout en conservant une progression totalement indépendante.

### Créer un profil
1. Cliquez sur le sélecteur de profil en haut à gauche de la barre de titre.
2. Cliquez sur **« Nouveau profil »** (ou l'icône `+`).
3. Saisissez le prénom de l'enfant, choisissez un avatar parmi les thèmes proposés (animaux, aventuriers, astronautes).
4. Définissez son **niveau de départ scolaire** (CE1, CE2, CM1, CM2). Ce niveau adapte automatiquement le seuil de difficulté initial et les tables recommandées.
5. Validez avec **Enregistrer**.

### Modifier ou supprimer un profil
- Dans le menu de sélection de profil, cliquez sur l'icône de crayon pour modifier l'avatar, le nom ou réajuster le niveau de départ.
- Vous pouvez également réinitialiser la progression d'un profil sans supprimer l'utilisateur.

---

## Les Modes de Jeu

La navigation s'effectue via la barre d'onglets située au bas de la fenêtre.

### 1. L'Aventure Galactique
Le mode aventure propose un voyage planétaire où chaque monde correspond à un palier de difficulté :
- **Monde 1 (Terre / Découverte)** : Tables de 1, 2 et 10 (idéal CE1).
- **Monde 2 (Lune / Explorateur)** : Tables de 3, 4 et 5 (CE1-CE2).
- **Monde 3 (Mars / Aventurier)** : Tables de 6 et 7 (CE2-CM1).
- **Monde 4 (Jupiter / Maître des Étoiles)** : Tables de 8 et 9 (CM1-CM2).
- **Monde 5 (Nébuleuse Mystère / Champion Suprême)** : Mix complet de 1 à 10 et défis de vitesse.

Chaque niveau réussi débloque des étoiles de bravoure et des trophées d'explorateur !

### 2. Le Dojo d'Entraînement
Le Dojo permet un travail ciblé et sans stress sur une ou plusieurs tables précises :
- Cochez les tables que l'enfant souhaite réviser (ex: seulement la table de 7 et de 8).
- Choisissez le type de test : **QCM** (4 propositions) ou **Saisie Libre** (pavé numérique).
- Aucune limite de temps : idéal pour mémoriser sereinement et comprendre le principe additif.

### 3. Le Chrono 60s
Le défi ultime pour tester ses réflexes et sa fluidité de calcul :
- Le joueur dispose de 60 secondes pour résoudre un maximum d'opérations.
- Chaque bonne réponse ajoute un bonus au score.
- Les records personnels sont enregistrés pour stimuler la progression.

### 4. La Table de Pythagore Interactive
Un outil visuel indispensable pour comprendre la structure matricielle de la multiplication et la propriété de commutativité ($a \times b = b \times a$) :
- Cliquez ou survolez une case pour illuminer la ligne et la colonne correspondantes.
- Observez le code couleur de maîtrise : les cases bien réussies s'allument en vert, tandis que celles nécessitant un entraînement ressortent en ambre.

---

## Types de Saisie et Raccourcis Clavier

L'application a été optimisée pour une ergonomie maximale sur ordinateur de bureau et portable :

1. **Mode QCM** :
   - Cliquez avec la souris ou l'écran tactile sur l'une des 4 réponses.
   - Les raccourcis clavier **1**, **2**, **3**, **4** permettent de choisir immédiatement la réponse associée.

2. **Mode Saisie Libre (Pavé Numérique)** :
   - Vous pouvez cliquer sur les chiffres à l'écran.
   - **Clavier physique** : Tapez directement les chiffres au clavier (pavé numérique ou rangée du haut).
   - **Touche Entrée / Enter / Pavé Entrée (`Return` / `KP_Enter`)** : Valide automatiquement la réponse saisie.
   - **Touche Retour Arrière (`Backspace`)** : Efface le dernier chiffre saisi.

---

## Statistiques et Récompenses

Dans la vue de profil et les bilans de session :
- Visualisez le taux de précision global et le temps de réponse moyen.
- Consultez la « carte de chaleur » pour identifier d'un coup d'œil les multiplications hésitantes.
- Collectionnez les 15 trophées du jeu (ex: *Éclair d'or*, *Ceinture noire du dojo*, *Sans faute*).

---

## Personnalisation et Préférences

Accédez aux préférences via le bouton de menu (trois points en haut à droite) :
- **Langue** : Français, Anglais, Espagnol, Allemand (changement instantané sans redémarrage).
- **Audio et Effets Sonores** : Activez ou ajustez le volume des effets sonores lors des succès.
- **Thème Visuel** : Respecte automatiquement le mode clair ou sombre de GNOME / Adwaita.
- **Licence & Open Source** : Consultez les détails de la licence Apache 2.0 et accédez directement au dépôt GitHub du projet.
