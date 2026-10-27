"""
Tests unitaires pour les modèles, la persistance et les profils.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multipli.models import Profile, StorageManager


class TestModels(unittest.TestCase):
    def setUp(self):
        self.profile = Profile(name="Alice", avatar="🐼", start_level="ce2")

    def test_profile_initialization(self):
        self.assertEqual(self.profile.name, "Alice")
        self.assertEqual(self.profile.avatar, "🐼")
        self.assertEqual(self.profile.start_level, "ce2")
        self.assertEqual(self.profile.chrono_best, 0)
        self.assertEqual(self.profile.total_answered, 0)
        self.assertEqual(self.profile.total_correct, 0)

    def test_record_answer_accuracy_and_stats(self):
        self.profile.record_answer(7, is_correct=True)
        self.assertEqual(self.profile.total_answered, 1)
        self.assertEqual(self.profile.total_correct, 1)
        self.assertEqual(self.profile.table_stats["7"]["correct"], 1)
        self.assertEqual(self.profile.table_stats["7"]["total"], 1)
        self.assertIn("first_win", self.profile.trophies)

        self.profile.record_answer(7, is_correct=False)
        self.assertEqual(self.profile.total_answered, 2)
        self.assertEqual(self.profile.total_correct, 1)
        self.assertEqual(self.profile.table_stats["7"]["correct"], 1)
        self.assertEqual(self.profile.table_stats["7"]["total"], 2)

    def test_record_streak_trophy(self):
        self.profile.record_streak(10)
        self.assertIn("streak_10", self.profile.trophies)

    def test_record_chrono(self):
        is_rec1 = self.profile.record_chrono(12)
        self.assertTrue(is_rec1)
        self.assertEqual(self.profile.chrono_best, 12)

        is_rec2 = self.profile.record_chrono(10)
        self.assertFalse(is_rec2)
        self.assertEqual(self.profile.chrono_best, 12)

        is_rec3 = self.profile.record_chrono(16)
        self.assertTrue(is_rec3)
        self.assertEqual(self.profile.chrono_best, 16)
        self.assertIn("chrono_15", self.profile.trophies)

    def test_update_level_stars(self):
        self.profile.update_level_stars("ce1", 3)
        self.assertEqual(self.profile.stars["ce1"], 3)
        self.assertIn("all_stars_ce1", self.profile.trophies)

        # Les étoiles ne régressent pas
        self.profile.update_level_stars("ce1", 1)
        self.assertEqual(self.profile.stars["ce1"], 3)

        self.profile.update_level_stars("cm2", 3)
        self.assertIn("all_stars_cm2", self.profile.trophies)

    def test_serialization_cycle(self):
        data = self.profile.to_dict()
        restored = Profile.from_dict(data)
        self.assertEqual(restored.name, self.profile.name)
        self.assertEqual(restored.avatar, self.profile.avatar)
        self.assertEqual(restored.start_level, self.profile.start_level)
        self.assertEqual(restored.chrono_best, self.profile.chrono_best)
        self.assertEqual(restored.trophies, self.profile.trophies)

    def test_profile_update(self):
        self.profile.update("Alice New", "🚀", "cm1")
        self.assertEqual(self.profile.name, "Alice New")
        self.assertEqual(self.profile.avatar, "🚀")
        self.assertEqual(self.profile.start_level, "cm1")

    def test_storage_manager_crud(self):
        sm = StorageManager.get_instance()
        initial_count = len(sm.profiles)

        p = sm.add_profile("TestChild", avatar="🦄", start_level="cm1")
        self.assertEqual(len(sm.profiles), initial_count + 1)
        self.assertEqual(sm.active_profile_id, p.id)

        sm.update_profile(p.id, name="TestChildRenamed", avatar="🐱", start_level="cm2")
        fetched = sm.get_profile(p.id)
        self.assertEqual(fetched.name, "TestChildRenamed")
        self.assertEqual(fetched.avatar, "🐱")
        self.assertEqual(fetched.start_level, "cm2")

        # Suppression
        sm.delete_profile(p.id)
        self.assertEqual(len(sm.profiles), initial_count)


if __name__ == "__main__":
    unittest.main()
