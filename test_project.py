"""
test_project.py

Minimal unittest suite for the earthquake project.
"""

from unittest import TestCase

from earthquakes.earthquakes import create_earthquake_db, query_db, read_bounding_box


class TestEarthquakeProject(TestCase):
    """Test suite for bounding box and database querying."""

    @classmethod
    def setUpClass(cls) -> None:
        """
        Build a small database once for all tests.
        Keeping it small makes tests faster and more reliable.
        """
        create_earthquake_db(days=7)

    def test_bounding_box(self) -> None:
        """Check that Padova, Parma, and Palermo are inside the bounding box."""
        box = read_bounding_box()

        cities = {
            "Padova": (45.4064, 11.8768),
            "Parma": (44.8015, 10.3279),
            "Palermo": (38.1157, 13.3615),
        }

        for city, (lat, lon) in cities.items():
            with self.subTest(city=city):
                self.assertTrue(box["minlatitude"] <= lat <= box["maxlatitude"])
                self.assertTrue(box["minlongitude"] <= lon <= box["maxlongitude"])

    def test_magnitude(self) -> None:
        """Check that no earthquake has magnitude > 9.5 (historical max)."""
        results = query_db(k=1000, days=3650, min_magnitude=0.0)
        for row in results:
            mag = row[2]
            self.assertLessEqual(mag, 9.5)

    def test_order(self) -> None:
        """Check that query_db returns earthquakes ordered by decreasing magnitude."""
        results = query_db(k=50, days=3650, min_magnitude=0.0)
        mags = [row[2] for row in results]
        self.assertEqual(mags, sorted(mags, reverse=True))

    def test_respects_k(self) -> None:
        """Extra test: query_db should return at most K rows."""
        k = 5
        results = query_db(k=k, days=3650, min_magnitude=0.0)
        self.assertLessEqual(len(results), k)