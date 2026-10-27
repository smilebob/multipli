"""
Gestion des données, profils de joueurs, statistiques et trophées.
Stocke les données dans ~/.local/share/multipli/data.json conformément aux standards XDG.
"""

import json
import os
import uuid
from typing import Dict, List, Optional


class Profile:
    def __init__(
        self,
        name: str = "Élève",
        avatar: str = "🦊",
        start_level: str = "ce1",
        profile_id: Optional[str] = None,
        stars: Optional[Dict[str, int]] = None,
        chrono_best: int = 0,
        total_answered: int = 0,
        total_correct: int = 0,
        table_stats: Optional[Dict[str, Dict[str, int]]] = None,
        trophies: Optional[List[str]] = None,
    ):
        self.id = profile_id or str(uuid.uuid4())[:8]
        self.name = name
        self.avatar = avatar
        self.start_level = start_level if start_level in ["ce1", "ce2", "cm1", "cm2"] else "ce1"
        self.stars = stars or {"ce1": 0, "ce2": 0, "cm1": 0, "cm2": 0}
        self.chrono_best = chrono_best
        self.total_answered = total_answered
        self.total_correct = total_correct
        # Statistique par table de 1 à 12 : {"correct": X, "total": Y}
        self.table_stats = table_stats or {str(i): {"correct": 0, "total": 0} for i in range(1, 13)}
        self.trophies = trophies or []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "avatar": self.avatar,
            "start_level": self.start_level,
            "stars": self.stars,
            "chrono_best": self.chrono_best,
            "total_answered": self.total_answered,
            "total_correct": self.total_correct,
            "table_stats": self.table_stats,
            "trophies": self.trophies,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Profile":
        return cls(
            name=data.get("name", "Élève"),
            avatar=data.get("avatar", "🦊"),
            start_level=data.get("start_level", "ce1"),
            profile_id=data.get("id"),
            stars=data.get("stars"),
            chrono_best=data.get("chrono_best", 0),
            total_answered=data.get("total_answered", 0),
            total_correct=data.get("total_correct", 0),
            table_stats=data.get("table_stats"),
            trophies=data.get("trophies"),
        )

    def update(self, name: str, avatar: str, start_level: str):
        self.name = name
        self.avatar = avatar
        if start_level in ["ce1", "ce2", "cm1", "cm2"]:
            self.start_level = start_level

    def record_answer(self, table: int, is_correct: bool):
        self.total_answered += 1
        if is_correct:
            self.total_correct += 1

        t_key = str(table)
        if t_key not in self.table_stats:
            self.table_stats[t_key] = {"correct": 0, "total": 0}
        self.table_stats[t_key]["total"] += 1
        if is_correct:
            self.table_stats[t_key]["correct"] += 1

        # Vérification trophée premier pas
        if self.total_correct >= 1 and "first_win" not in self.trophies:
            self.trophies.append("first_win")

    def record_streak(self, streak: int):
        if streak >= 10 and "streak_10" not in self.trophies:
            self.trophies.append("streak_10")

    def record_chrono(self, score: int) -> bool:
        """Enregistre un score chrono et retourne True s'il s'agit d'un nouveau record."""
        is_new_record = False
        if score > self.chrono_best:
            self.chrono_best = score
            is_new_record = True

        if score >= 15 and "chrono_15" not in self.trophies:
            self.trophies.append("chrono_15")

        return is_new_record

    def update_level_stars(self, level_id: str, stars: int):
        current = self.stars.get(level_id, 0)
        if stars > current:
            self.stars[level_id] = stars

        if self.stars.get("ce1", 0) >= 3 and "all_stars_ce1" not in self.trophies:
            self.trophies.append("all_stars_ce1")
        if self.stars.get("cm2", 0) >= 3 and "all_stars_cm2" not in self.trophies:
            self.trophies.append("all_stars_cm2")


class StorageManager:
    _instance = None

    def __init__(self):
        xdg_data = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        self.data_dir = os.path.join(xdg_data, "multipli")
        os.makedirs(self.data_dir, exist_ok=True)
        self.filepath = os.path.join(self.data_dir, "data.json")

        self.profiles: List[Profile] = []
        self.active_profile_id: Optional[str] = None
        self.settings: dict = {
            "language": "fr",
            "sound_enabled": True,
        }

        self.load()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = StorageManager()
        return cls._instance

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.settings = data.get("settings", self.settings)
                    self.active_profile_id = data.get("active_profile_id")
                    self.profiles = [Profile.from_dict(p) for p in data.get("profiles", [])]
            except Exception as e:
                print(f"Erreur chargement données {self.filepath}: {e}")

        # S'il n'y a pas de profil, créer un profil par défaut
        if not self.profiles:
            default_p = Profile(name="Élève", avatar="🦊")
            self.profiles.append(default_p)
            self.active_profile_id = default_p.id
            self.save()

        if self.active_profile_id is None or not self.get_profile(self.active_profile_id):
            self.active_profile_id = self.profiles[0].id

    def save(self):
        try:
            data = {
                "settings": self.settings,
                "active_profile_id": self.active_profile_id,
                "profiles": [p.to_dict() for p in self.profiles],
            }
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde données {self.filepath}: {e}")

    def get_active_profile(self) -> Profile:
        p = self.get_profile(self.active_profile_id)
        if p:
            return p
        return self.profiles[0]

    def get_profile(self, profile_id: Optional[str]) -> Optional[Profile]:
        for p in self.profiles:
            if p.id == profile_id:
                return p
        return None

    def add_profile(self, name: str, avatar: str = "🦊", start_level: str = "ce1") -> Profile:
        p = Profile(name=name, avatar=avatar, start_level=start_level)
        self.profiles.append(p)
        self.active_profile_id = p.id
        self.save()
        return p

    def update_profile(self, profile_id: str, name: str, avatar: str, start_level: str) -> bool:
        p = self.get_profile(profile_id)
        if not p:
            return False
        p.update(name=name, avatar=avatar, start_level=start_level)
        self.save()
        return True

    def delete_profile(self, profile_id: str) -> bool:
        if len(self.profiles) <= 1:
            return False  # Garder au moins un profil
        self.profiles = [p for p in self.profiles if p.id != profile_id]
        if self.active_profile_id == profile_id:
            self.active_profile_id = self.profiles[0].id
        self.save()
        return True

    def set_active_profile(self, profile_id: str):
        if self.get_profile(profile_id):
            self.active_profile_id = profile_id
            self.save()
