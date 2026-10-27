"""
Système internationalisation (i18n) modulaire pour Multipli.
Charge dynamiquement les fichiers JSON du dossier locales/.
Permet d'ajouter une langue simplement en ajoutant un nouveau fichier .json !
"""

import json
import os
from typing import Callable, Dict, List, Tuple


class I18n:
    _instance = None

    def __init__(self, locales_dir: str = None):
        if locales_dir is None:
            # Emplacement par défaut : dossier ../locales par rapport à ce fichier
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            locales_dir = os.path.join(base_dir, "locales")
            if not os.path.isdir(locales_dir):
                # Fallback système (/usr/share/multipli/locales)
                locales_dir = "/usr/share/multipli/locales"

        self.locales_dir = locales_dir
        self.current_lang = "fr"
        self.translations: Dict[str, Dict[str, str]] = {}
        self._listeners: List[Callable[[str], None]] = []

        self.reload_languages()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = I18n()
        return cls._instance

    def reload_languages(self):
        """Scanne le répertoire locales/ et recharge tous les fichiers JSON disponibles."""
        self.translations.clear()
        if not os.path.isdir(self.locales_dir):
            return

        for filename in sorted(os.listdir(self.locales_dir)):
            if filename.endswith(".json"):
                lang_code = filename[:-5]
                filepath = os.path.join(self.locales_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.translations[lang_code] = data
                except Exception as e:
                    print(f"Erreur chargement langue {filename}: {e}")

    def get_available_languages(self) -> List[Tuple[str, str, str]]:
        """Retourne la liste des langues disponibles : [(code, nom, drapeau), ...]"""
        result = []
        for code, data in self.translations.items():
            name = data.get("lang_name", code.upper())
            flag = data.get("lang_flag", "🌐")
            result.append((code, name, flag))
        return result

    def set_language(self, lang_code: str):
        """Change la langue active et notifie tous les écouteurs."""
        if lang_code in self.translations and lang_code != self.current_lang:
            self.current_lang = lang_code
            for callback in self._listeners:
                try:
                    callback(lang_code)
                except Exception as e:
                    print(f"Erreur callback langue: {e}")

    def add_listener(self, callback: Callable[[str], None]):
        """Abonne un widget ou une vue aux changements de langue."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[str], None]):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def t(self, key: str, **kwargs) -> str:
        """Traduit une clé avec substitution éventuelle de variables."""
        curr_dict = self.translations.get(self.current_lang, {})
        text = curr_dict.get(key)

        if text is None:
            # Fallback en français
            fr_dict = self.translations.get("fr", {})
            text = fr_dict.get(key)

        if text is None:
            # Fallback en anglais
            en_dict = self.translations.get("en", {})
            text = en_dict.get(key)

        if text is None:
            return key

        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text


# Helper global pratique
def _(key: str, **kwargs) -> str:
    return I18n.get_instance().t(key, **kwargs)
