import open3d as o3d
import numpy as np
import json
import random
from scipy.spatial import KDTree

def main(ply_path):
    # Ścieżki do plików
    points_within_objects_path = 'points_within_objects.json'  # Plik JSON z punktami wewnątrz obiektów
    bounding_box_path = 'bounding_boxes.json'  # Plik JSON z bounding boxami obiektów
    color_class_mapping_path = 'color_class_mapping.json'  # Plik JSON z mapowaniem kolorów do klas

    # Wczytanie oryginalnej chmury punktów
    pcd = o3d.io.read_point_cloud(ply_path)

    # Konwersja chmury punktów do macierzy NumPy (punkty i kolory)
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors) if pcd.has_colors() else np.full((points.shape[0], 3), 1.0)  # Domyślne białe kolory (w skali 0-1)

    # Wczytanie danych o punktach wewnątrz obiektów z przypisanymi klasami
    with open(points_within_objects_path, 'r') as json_file:
        points_within_objects = json.load(json_file)

    # Przygotowanie kolorów dla każdej klasy obiektów
    class_colors = {}
    unique_classes = set(obj['class'] for obj in points_within_objects)

    for class_name in unique_classes:
        # Losowanie unikalnego koloru dla każdej klasy w skali 0-1
        class_colors[class_name] = [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)]

    # Stworzenie KD-Tree do efektywnego znajdowania najbliższych punktów
    kd_tree = KDTree(points)

    # Iteracja przez punkty w JSON i znajdowanie najbliższego punktu w chmurze
    for point_data in points_within_objects:
        point_3D = point_data['point_3D']
        object_class = point_data['class']

        # Punkt 3D jako macierz NumPy
        query_point = np.array([point_3D['x'], point_3D['y'], point_3D['z']])

        # Znalezienie najbliższego punktu w chmurze przy użyciu KD-Tree
        distance, index = kd_tree.query(query_point)

        # Ustalamy maksymalną tolerancję dla dopasowania punktu
        if distance < 0.01:  # Tolerancja: 0.01 jednostki
            colors[index] = class_colors[object_class]

    # Aktualizacja kolorów w chmurze punktów
    pcd.colors = o3d.utility.Vector3dVector(colors)

    # Zapisanie chmury punktów do nowego pliku PLY z nowymi kolorami
    output_ply_path = 'chmura_pokolorowana.ply'
    o3d.io.write_point_cloud(output_ply_path, pcd)

    print(f"Chmura punktów została zapisana do pliku '{output_ply_path}' z nowymi kolorami.")

    # Zapisanie mapowania kolorów do klas do pliku JSON
    color_class_mapping = {
        class_name: {
            "color": {
                "r": class_colors[class_name][0],
                "g": class_colors[class_name][1],
                "b": class_colors[class_name][2]
            }
        }
        for class_name in class_colors
    }

    with open(color_class_mapping_path, 'w') as json_file:
        json.dump(color_class_mapping, json_file, indent=4)

    print(f"Mapowanie kolorów do klas zostało zapisane do pliku '{color_class_mapping_path}'.")


if __name__ == "__main__":
    main()
