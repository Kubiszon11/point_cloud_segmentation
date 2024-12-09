import open3d as o3d
import numpy as np
import cv2
import matplotlib.pyplot as plt
import json

def main(ply_path):
    # Parametry intrinsic dla lewego sensora kamery (należy dostosować indywidualnie)
    K_left = np.array([[1071.2400, 0, 1107.4200],
                       [0, 1071.0100, 621.3260],
                       [0, 0, 1]])

    # Parametry zniekształceń dla lewego sensora (należy dostosować indywidualnie)
    dist_left = np.array([-1.1838, 2.3461, 0.0001, -0.0000, 0.1203])

    # Wczytanie chmury punktów z pliku .ply za pomocą Open3D
    pcd = o3d.io.read_point_cloud(ply_path)

    # Sprawdzenie, czy chmura punktów została poprawnie wczytana
    if not pcd.has_points():
        print("Błąd: Nie udało się wczytać chmury punktów z pliku.")
        return

    # Wizualizacja wczytanej chmury punktów za pomocą Open3D
    # print("Wizualizacja wczytanej chmury punktów z kolorami")
    # o3d.visualization.draw_geometries([pcd])

    # Konwersja chmury punktów do macierzy NumPy
    points = np.asarray(pcd.points)

    # Sprawdzenie, czy chmura punktów zawiera informacje o kolorach
    if pcd.has_colors():
        colors = np.asarray(pcd.colors)
    else:
        print("Brak informacji o kolorach w chmurze punktów.")
        colors = np.full((points.shape[0], 3), 255)  # Domyślnie białe punkty, jeśli brak kolorów

    # Założenie braku rotacji i translacji (kamera w pozycji początkowej)
    R = np.eye(3)  # Macierz rotacji (jednostkowa)
    t = np.zeros((3, 1))  # Wektor translacji (zerowy)

    # Rzutowanie punktów 3D na płaszczyznę obrazu kamery
    # OpenCV wymaga punktów w kształcie (N, 1, 3) do funkcji cv2.projectPoints, więc należy zmienić kształt
    points_3D = points.reshape(-1, 1, 3).astype(np.float32)

    # Rzutowanie przy użyciu OpenCV
    points_2D, _ = cv2.projectPoints(points_3D, R, t, K_left, dist_left)

    # Przekształcenie wynikowych punktów do wygodnego formatu
    points_2D = points_2D.reshape(-1, 2)

    # Przygotowanie pustego obrazu o rozmiarze Full HD (można dostosować rozdzielczość do swoich potrzeb)
    output_image = np.zeros((1080, 1920, 3), dtype=np.uint8)

    # Inicjalizacja słownika do przechowywania powiązań punktów 3D -> 2D
    mapping = []

    # Rysowanie punktów na obrazie z uwzględnieniem kolorów
    for i, (point_3D, point_2D) in enumerate(zip(points_3D, points_2D)):
        x, y = int(point_2D[0]), int(point_2D[1])
        # Sprawdzanie, czy punkt znajduje się w obrębie obrazu
        if 0 <= x < output_image.shape[1] and 0 <= y < output_image.shape[0]:
            color = (int(colors[i][2] * 255), int(colors[i][1] * 255), int(colors[i][0] * 255))  # Kolory w BGR
            cv2.circle(output_image, (x, y), 2, color, -1)  # Rysowanie punktu o odpowiednim kolorze

            # Zapisanie powiązania punktu 3D -> 2D do słownika
            mapping.append({
                "point_3D": {
                    "x": float(point_3D[0][0]),
                    "y": float(point_3D[0][1]),
                    "z": float(point_3D[0][2])
                },
                "point_2D": {
                    "x": x,
                    "y": y
                }
            })

    # Zapisanie mapowania do pliku JSON
    with open('mapping.json', 'w') as json_file:
        json.dump(mapping, json_file, indent=4)

    print("Powiązanie punktów 3D z pikselami 2D zostało zapisane jako 'mapping.json'.")

    # Zapisanie obrazu do pliku PNG
    cv2.imwrite('rzutowana_chmura_punktow_kolor.png', output_image)
    print("Obraz został zapisany jako 'rzutowana_chmura_punktow_kolor.png'")

    # # Przekształcenie obrazu z formatu BGR (OpenCV) do RGB (matplotlib)
    # output_image_rgb = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
    #
    # # Wyświetlenie obrazu za pomocą matplotlib
    # plt.imshow(output_image_rgb)
    # plt.title("Rzutowana chmura punktów")
    # plt.axis('off')  # Wyłączenie osi
    # plt.show()

if __name__ == "__main__":
    main()
