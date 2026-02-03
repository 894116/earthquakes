

"""
test_project.py

Test suite for the earthquakes project using unittest.
"""

import os
import tempfile
from unittest import TestCase

from earthquakes.earthquakes import create_earthquake_db, query_db, read_bounding_box


class TestEarthquakeProject(TestCase):
    """Test suite for the earthquake project."""

    def setUp(self):
        """
        Create a temporary SQLite database for each test,
        and populate it with a small deterministic dataset.
        """
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self._tmpdir.name, "test_earthquakes.db")

        # (day, time, mag, latitude, longitude, place)
        self.sample_rows = [
            ("2026-01-01", "10:00:00", 4.2, 45.0, 11.0, "Test A"),
            ("2026-01-02", "11:00:00", 2.1, 44.0, 10.0, "Test B"),
            ("2026-01-03", "12:00:00", 6.5, 43.0, 12.0, "Test C"),
            ("2026-01-04", "13:00:00", 9.5, 42.0, 13.0, "Test D"),
        ]

        create_earthquake_db(self.sample_rows, db_path=self.db_path)

    def tearDown(self):
        """Cleanup the temporary directory and database."""
        self._tmpdir.cleanup()

    def test_bounding_box(self):
        """
        Check that Padova, Parma, and Palermo are inside the bounding box.
        """
        bounding_box = read_bounding_box()

        # Coordinates: (latitude, longitude)
        cities = {
            "Padova": (45.4064, 11.8768),
            "Parma": (44.8015, 10.3279),
            "Palermo": (38.1157, 13.3615),
        }

        for city, (lat, lon) in cities.items():
            with self.subTest(city=city):
                self.assertGreaterEqual(lat, bounding_box["minlatitude"])
                self.assertLessEqual(lat, bounding_box["maxlatitude"])
                self.assertGreaterEqual(lon, bounding_box["minlongitude"])
                self.assertLessEqual(lon, bounding_box["maxlongitude"])

    def test_magnitude(self):
        """
        Check that no earthquake has magnitude > 9.5.
        """
        results = query_db(
            k=1000,
            days=36500,
            min_magnitude=0.0,
            db_path=self.db_path,
        )

        for _, _, mag, _, _, _ in results:
            self.assertLessEqual(mag, 9.5)

    def test_order(self):
        """
        Check that query_db returns earthquakes ordered by decreasing magnitude.
        """
        results = query_db(
            k=50,
            days=36500,
            min_magnitude=0.0,
            db_path=self.db_path,
        )

        magnitudes = [row[2] for row in results]
        self.assertEqual(magnitudes, sorted(magnitudes, reverse=True))