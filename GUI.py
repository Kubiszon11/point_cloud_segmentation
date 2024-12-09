import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD  # Biblioteka do obsługi przeciągania i upuszczania plików
from PIL import Image, ImageTk  # Dla pracy z obrazami
import open3d as o3d
import os
import projection
import interior_complement_bb
import instance_segmentation_bb
import visualization
import threading
import time


class PointCloudApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikacja do segmentacji obiektów na podstawie chmuy punktów")

        # Ścieżka do pliku chmury punktów
        self.ply_path = None

        # Przyciski GUI
        self.load_button = tk.Button(root, text="Załaduj chmurę punktów (.ply)", command=self.load_ply)
        self.load_button.pack(pady=10)

        self.run_button = tk.Button(root, text="Rozpocznij przetwarzanie", command=self.run_processing, state=tk.DISABLED)
        self.run_button.pack(pady=10)

        self.save_button = tk.Button(root, text="Zapisz wynikową chmurę punktów", command=self.save_ply, state=tk.DISABLED)
        self.save_button.pack(pady=10)

        # Wizualizacja chmury punktów
        #self.visualize_button = tk.Button(root, text="Visualize Point Cloud", command=self.visualize_ply, state=tk.DISABLED)
        #self.visualize_button.pack(pady=10)

        # Obszar przeciągania i upuszczania plików
        self.drop_area = tk.Label(root, text="Upuść tutaj plik .ply", relief="groove", width=40, height=5)
        self.drop_area.pack(pady=10)

        # Konfiguracja przeciągania i upuszczania plików
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

        # Pasek postępu
        self.progress = ttk.Progressbar(root, mode='indeterminate')

        # Canvas do wyświetlania obrazów w trakcie przetwarzania
        self.canvas = tk.Canvas(root, width=640, height=480)
        self.canvas.pack(pady=10)

        # Przycisk "Zamknij" do zakończenia programu
        self.close_button = tk.Button(root, text="Zamknij", command=self.close_application)
        self.close_button.pack(pady=10)

    def on_drop(self, event):
        file_path = event.data.strip('{}')  # Usuwamy nawiasy klamrowe z ścieżki
        if file_path.endswith('.ply'):
            self.ply_path = file_path
            messagebox.showinfo("Info", f"Załadowana chmura punktów: {os.path.basename(self.ply_path)}")
            self.run_button.config(state=tk.NORMAL)
            #self.visualize_button.config(state=tk.NORMAL)
        else:
            messagebox.showerror("Error", "Only .ply files are supported.")

    def load_ply(self):
        # Wybór pliku .ply
        self.ply_path = filedialog.askopenfilename(filetypes=[("PLY files", "*.ply")])
        if self.ply_path:
            messagebox.showinfo("Info", f"Załadowana chmura punktów: {os.path.basename(self.ply_path)}")
            self.run_button.config(state=tk.NORMAL)
            #self.visualize_button.config(state=tk.NORMAL)

    def run_processing(self):
        if self.ply_path:
            # Uruchomienie przetwarzania w osobnym wątku
            self.progress.pack(pady=10)
            self.progress.start()
            threading.Thread(target=self.process_point_cloud).start()

    def process_point_cloud(self):
        try:
            start_time = time.time()

            # Etap 1: Rzutowanie
            projection_start = time.time()
            self.show_image('rozpoczeto_proces.png')
            projection.main(self.ply_path)  # Przekazanie ścieżki do rzutowania
            self.show_image('rzutowana_chmura_punktow_kolor.png')  # Pokaż wynik rzutowania
            projection_end = time.time()
            print(f"Czas wykonania modułu 'projection': {projection_end - projection_start:.2f} sekund")

            instance_segmentation_start = time.time()
            # Etap 2: Segmentacja instancji
            instance_segmentation_bb.main()
            self.show_image('segmented_with_boxes.jpg')  # Pokaż wynik segmentacji
            instance_segmentation_end = time.time()
            print(
                f"Czas wykonania modułu 'instance_segmentation': {instance_segmentation_end - instance_segmentation_start:.2f} sekund")

            uzupelnienie_wnetrza_start = time.time()
            # # Etap 3: Uzupełnienie wnętrza
            interior_complement_bb.main()
            # self.show_image('completed_interior_image.jpg')  # Pokaż wynik uzupełniania wnętrza
            uzupelnienie_wnetrza_end = time.time()
            print(
                f"Czas wykonania modułu 'uzupelnienie_wnetrza': {uzupelnienie_wnetrza_end - uzupelnienie_wnetrza_start:.2f} sekund")
            #
            kolorowanie_obiektow_start = time.time()
            # # Etap 4: Kolorowanie obiektów
            visualization.main(self.ply_path)
            # self.show_image('colored_image.jpg')  # Pokaż wynik kolorowania
            kolorowanie_obiektow_end = time.time()
            print(
                f"Czas wykonania modułu 'kolorowanie_obiektow': {kolorowanie_obiektow_end - kolorowanie_obiektow_start:.2f} sekund")

            # Zapisanie czasu zakończenia programu
            end_time = time.time()

            # Obliczenie całkowitego czasu wykonania programu
            elapsed_time = end_time - start_time
            print(f"Czas wykonania całego programu: {elapsed_time:.2f} sekund")

            messagebox.showinfo("Info", "Przetwarzanie zakończone pomyślnie!")
            self.save_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during processing: {str(e)}")
        finally:
            self.progress.stop()
            self.progress.pack_forget()

    def show_image(self, image_path):
        """Pomocnicza funkcja do wyświetlania obrazów na Canvas"""
        try:
            # Załaduj obraz
            img = Image.open(image_path)
            img = img.resize((640, 480))  # Dostosowanie rozmiaru obrazu do canvasu
            img_tk = ImageTk.PhotoImage(img)

            # Wyczyść Canvas przed wyświetleniem nowego obrazu
            self.canvas.delete("all")

            # Wyświetl obraz na Canvas
            self.canvas.create_image(0, 0, anchor="nw", image=img_tk)

            # Przechowaj referencję do obiektu obrazu (konieczne do wyświetlenia)
            self.canvas.image = img_tk
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while displaying image: {str(e)}")

    def save_ply(self):
        # Zapisanie wynikowej chmury punktów
        save_path = filedialog.asksaveasfilename(defaultextension=".ply", filetypes=[("PLY files", "*.ply")])
        if save_path:
            try:
                # Zakładamy, że wynikowa chmura punktów jest zapisywana w pliku 'chmura_pokolorowana.ply'
                result_ply_path = 'chmura_pokolorowana.ply'
                if os.path.exists(result_ply_path):
                    os.rename(result_ply_path, save_path)
                    messagebox.showinfo("Info", f"Zapisano wynikową chmurę punktów w: {save_path}")
                else:
                    messagebox.showerror("Error", "Resulting point cloud file not found.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while saving: {str(e)}")

    def visualize_ply(self):
        if self.ply_path:
            try:
                # Wczytanie i wizualizacja chmury punktów za pomocą Open3D
                pcd = o3d.io.read_point_cloud(self.ply_path)
                o3d.visualization.draw_geometries([pcd])
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during visualization: {str(e)}")

    def close_application(self):
        """Zamyka aplikację"""
        self.root.quit()

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Inicjalizacja TkinterDnD dla głównego okna
    app = PointCloudApp(root)
    root.mainloop()
