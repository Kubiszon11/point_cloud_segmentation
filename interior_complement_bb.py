import json
from shapely.geometry import Polygon, Point

def main():
    # Ścieżki do plików JSON
    mapping_path = 'mapping.json'  # Plik z mapowaniem punktów 3D -> 2D
    bounding_box_path = 'bounding_boxes.json'  # Plik z bounding boxami obiektów

    # Wczytanie mapowania punktów 3D -> 2D
    with open(mapping_path, 'r') as mapping_file:
        mapping = json.load(mapping_file)

    # Wczytanie danych o bounding boxach obiektów
    with open(bounding_box_path, 'r') as bounding_file:
        bounding_data = json.load(bounding_file)

    # Lista do przechowywania wynikowych punktów wewnątrz otoczek
    points_within_objects = []

    # Iteracja przez każdy bounding box
    for obj in bounding_data:
        bounding_box = obj['bounding_box']
        object_class = obj['class']

        # Definiowanie Bounding Box jako prostokąta (x, y, width, height)
        min_x = bounding_box['x'] - bounding_box['width'] / 2
        max_x = bounding_box['x'] + bounding_box['width'] / 2
        min_y = bounding_box['y'] - bounding_box['height'] / 2
        max_y = bounding_box['y'] + bounding_box['height'] / 2

        # Definiowanie obramowania obiektu jako wielokąta (Polygon) na podstawie punktów
        if 'points' in obj:
            polygon_points = [(point['x'], point['y']) for point in obj['points']]
            object_polygon = Polygon(polygon_points)
        else:
            print(f"Brak obramowania dla obiektu klasy {object_class}.")
            continue

        # Iteracja przez wszystkie punkty w mapping.json i sprawdzenie, które znajdują się wewnątrz Bounding Box
        for point_map in mapping:
            point_2D = point_map['point_2D']
            point_3D = point_map['point_3D']

            x, y = point_2D['x'], point_2D['y']

            # Sprawdzenie, czy punkt znajduje się wewnątrz Bounding Box
            if min_x <= x <= max_x and min_y <= y <= max_y:
                # Jeśli punkt jest w Bounding Boxie, sprawdzamy, czy jest też wewnątrz obramowania (wielokąta)
                point = Point(x, y)
                if object_polygon.contains(point):
                    # Dodajemy punkt do wynikowej listy wraz z przypisaną klasą
                    points_within_objects.append({
                        "class": object_class,
                        "point_3D": {
                            "x": point_3D['x'],
                            "y": point_3D['y'],
                            "z": point_3D['z']
                        },
                        "point_2D": {
                            "x": x,
                            "y": y
                        }
                    })

    # Zapisanie mapowania punktów wewnątrz bounding boxów do pliku JSON
    with open('points_within_objects.json', 'w') as json_file:
        json.dump(points_within_objects, json_file, indent=4)

    print("Informacje o punktach wewnątrz obramowania obiektów zostały zapisane do pliku 'points_within_objects.json'.")

if __name__ == "__main__":
    main()
