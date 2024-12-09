from roboflow import Roboflow
import cv2
import matplotlib.pyplot as plt
import json

def load_model():
    # Inicjalizacja Roboflow z kluczem API
    rf = Roboflow(api_key="c5QiVkbBQ24vcs0xzNpc")
    # Pobranie projektu i wersji modelu
    project = rf.workspace().project("inzynierka-cfwh7")
    model = project.version(1).model
    return model

def segment_image(model, image_path, output_path="segmented_image.jpg", json_output_path="segmented_points.json", boxed_image_output_path="segmented_with_boxes.jpg"):
    # Wykonanie predykcji na lokalnym obrazie i zapisanie wyniku w celu prezentacji użytkownikowi poprawności segmentacji na obrazie 2D
    prediction = model.predict(image_path, confidence=85) #roboflow
    #prediction = model.predict(image_path, confidence=31) #yolo11
    prediction.save(output_path)

    # Zapisanie punktów dookoła wykrytych obiektów do pliku JSON
    predictions_data = prediction.json()
    points_list = []
    bounding_boxes = []  # Lista na bounding boxy dla każdego obiektu

    for pred in predictions_data['predictions']:
        if 'points' in pred:
            points = pred['points']
            points_list.append({
                'class': pred['class'],
                'points': points
            })

        # Dodanie bounding box do listy
        if 'x' in pred and 'y' in pred and 'width' in pred and 'height' in pred:
            bounding_box = {
                'class': pred['class'],
                'bounding_box': {
                    'x': pred['x'],
                    'y': pred['y'],
                    'width': pred['width'],
                    'height': pred['height']
                }
            }

            # Dodanie punktów obramowania (jeśli dostępne) do bounding boxa
            if 'points' in pred:
                bounding_box['points'] = pred['points']

            bounding_boxes.append(bounding_box)

    # Zapisanie danych do pliku JSON
    with open(json_output_path, 'w') as json_file:
        json.dump(points_list, json_file, indent=4)

    # Zapisanie bounding boxów do osobnego pliku JSON
    with open('bounding_boxes.json', 'w') as json_file:
        json.dump(bounding_boxes, json_file, indent=4)

    # Wczytanie obrazu wynikowego
    segmented_image = cv2.imread(output_path)

    # Rysowanie bounding boxów na obrazie w celu wizaualizacji wyniku dla użytkownika
    for box in bounding_boxes:
        x_center = box['bounding_box']['x']
        y_center = box['bounding_box']['y']
        width = box['bounding_box']['width']
        height = box['bounding_box']['height']

        # Przeliczenie współrzędnych Bounding Boxa do postaci (x1, y1), (x2, y2)
        x1 = int(x_center - width / 2)
        y1 = int(y_center - height / 2)
        x2 = int(x_center + width / 2)
        y2 = int(y_center + height / 2)

        # Rysowanie prostokąta (Bounding Box) na obrazie
        cv2.rectangle(segmented_image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Zielony prostokąt z grubością linii 2
        cv2.putText(segmented_image, box['class'], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Rysowanie obramowania obiektu (wielokąta) na obrazie, jeśli dostępne
        if 'points' in box:
            points = box['points']
            for i in range(len(points)):
                # Rysowanie linii między kolejnymi punktami obramowania
                start_point = (int(points[i]['x']), int(points[i]['y']))
                end_point = (int(points[(i + 1) % len(points)]['x']), int(points[(i + 1) % len(points)]['y']))
                cv2.line(segmented_image, start_point, end_point, (255, 0, 0), 2)  # Niebieska linia o grubości 2

    # Zapisanie obrazu z narysowanymi bounding boxami
    cv2.imwrite(boxed_image_output_path, segmented_image)

    print(f"Obraz z zaznaczonymi bounding boxami zapisany w '{boxed_image_output_path}'.")

    return segmented_image

def display_image(image, title="Segmented Image"):
    # Wyświetlenie obrazu za pomocą matplotlib w celu weryfikacji dla projektanta
    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis("off")
    plt.show()

def main():
    # Ścieżka do obrazu wejściowego zapisanego w module "projection.py"
    image_path = "rzutowana_chmura_punktow_kolor.png"

    # Ścieżka do zapisu wyniku
    output_path = "segmented_image.jpg"
    json_output_path = "segmented_points.json"
    boxed_image_output_path = "segmented_with_boxes.jpg"

    # Załadowanie modelu
    model = load_model()

    # Segmentacja obrazu i zapisanie punktów do JSON
    segmented_image = segment_image(model, image_path, output_path, json_output_path, boxed_image_output_path)

    # Wyświetlenie obrazu
    # display_image(segmented_image)

    print(f"Obraz z segmentacją zapisany w {output_path}")
    print(f"Punkty segmentacji zapisane w {json_output_path}")

if __name__ == "__main__":
    main()
