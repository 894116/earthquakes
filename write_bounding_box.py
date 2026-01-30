import csv

bounding_box = {
'minlatitude': 35.0,
'maxlatitude': 47.5,
'minlongitude': 5.0,
'maxlongitude': 20.0
}

with open('bounding_box.csv', 'w', newline = '') as file:
    writer = csv.writer(file)
    writer.writerow(bounding_box.keys())
    writer.writerow(bounding_box.values())


