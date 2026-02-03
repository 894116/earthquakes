import os
import tempfile
import pytest

from earthquakes.earthquakes import read_bounding_box

#first test

def test_read_bounding_box_missing_columns():
    csv_content = (
        "minlatitude,maxlatitude\n"
        "35.0,47.5\n"
    )

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "bounding_box.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write(csv_content)

        with pytest.raises(ValueError):
            read_bounding_box(path)

#second test
def test_read_bounding_box_empty_file():
    csv_content = ""

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "bounding_box.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write(csv_content)

        with pytest.raises(ValueError):
            read_bounding_box(path)


from unittest.mock import Mock, patch

from earthquakes.earthquakes import gather_earthquakes


def test_gather_earthquakes_invalid_response_raises_value_error():
    fake_response = Mock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {"not_features": []}

    bounding_box = {
        "minlatitude": 35.0,
        "maxlatitude": 47.5,
        "minlongitude": 5.0,
        "maxlongitude": 20.0,
    }

    with patch("earthquakes.earthquakes.requests.get", return_value=fake_response):
        with pytest.raises(ValueError):
            gather_earthquakes(7, bounding_box)