import math
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, IntVar
from PIL import Image, ImageTk
import cv2
import matplotlib.pyplot as plt
from matplotlib import cm
import json
import random

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Area and Volume Calculator")
        self.sensor_angle_var = tk.StringVar()
        self.sensor_height_var = tk.StringVar()
        self.average_road_var = tk.StringVar()
        self.video_label = None
        self.cap = None
        self.results = []
        self.unit_var = IntVar()
        self.unit_var.set(0)
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        tab_calculation = ttk.Frame(notebook)
        notebook.add(tab_calculation, text="Calculation")
        self.create_calculation_widgets(tab_calculation)

        tab_visualization = ttk.Frame(notebook)
        notebook.add(tab_visualization, text="Visualization")
        self.create_visualization_widgets(tab_visualization)

        tab_save_export = ttk.Frame(notebook)
        notebook.add(tab_save_export, text="Save/Export")
        self.create_save_export_widgets(tab_save_export)

    def create_calculation_widgets(self, frame):
        sensor_angle_label = tk.Label(frame, text="Enter sensor angle in degrees:")
        sensor_angle_label.pack()

        sensor_angle_entry = tk.Entry(frame, textvariable=self.sensor_angle_var)
        sensor_angle_entry.pack(fill="x", padx=10, pady=5, expand=True)

        sensor_height_label = tk.Label(frame, text="Enter sensor height in meters:")
        sensor_height_label.pack()

        sensor_height_entry = tk.Entry(frame, textvariable=self.sensor_height_var)
        sensor_height_entry.pack(fill="x", padx=10, pady=5, expand=True)

        average_road_label = tk.Label(frame, text="Enter Average road height in meters:")
        average_road_label.pack()

        average_road_entry = tk.Entry(frame, textvariable=self.average_road_var)
        average_road_entry.pack(fill="x", padx=10, pady=5, expand=True)

        unit_label = tk.Label(frame, text="Select Units:")
        unit_label.pack()

        metric_radio = tk.Radiobutton(frame, text="Metric (meters, kilograms)", variable=self.unit_var, value=0)
        metric_radio.pack()

        imperial_radio = tk.Radiobutton(frame, text="Imperial (feet, pounds)", variable=self.unit_var, value=1)
        imperial_radio.pack()

        calculate_button = tk.Button(frame, text="Calculate", command=self.calculate)
        calculate_button.pack(padx=10, pady=10)

        self.result_text = tk.Text(frame, font=("Helvetica", 12), wrap=tk.WORD, height=10, width=40)
        self.result_text.pack(fill="both", padx=10, pady=5, expand=True)

        clear_result_button = tk.Button(frame, text="Clear Result", command=self.clear_result)
        clear_result_button.pack(padx=10, pady=10)

        generate_random_button = tk.Button(frame, text="Generate Random Inputs", command=self.generate_random_inputs)
        generate_random_button.pack(padx=10, pady=10)

    def create_visualization_widgets(self, frame):
        plot_2d_graph_button = tk.Button(frame, text="Plot 2D Graph", command=self.plot_2d_graph)
        plot_2d_graph_button.pack(padx=10, pady=10)

        display_3d_button = tk.Button(frame, text="Display 3D Visualization", command=self.display_3d_visualization)
        display_3d_button.pack(padx=10, pady=10)

        display_video_button = tk.Button(frame, text="Display Video", command=self.display_video)
        display_video_button.pack(padx=10, pady=10)

    def create_save_export_widgets(self, frame):
        save_results_button = tk.Button(frame, text="Save Results as JSON", command=self.save_results)
        save_results_button.pack(padx=10, pady=10)

        export_visualization_button = tk.Button(frame, text="Export Visualization as Image", command=self.export_visualization)
        export_visualization_button.pack(padx=10, pady=10)

    def calculate(self):
        try:
            sensor_width = float(self.sensor_angle_var.get())
            Beta_degrees = 90
            Beta_alpha = Beta_degrees + sensor_width
            Gamma = 180 - Beta_alpha
            alpha_radians = math.radians(sensor_width)

            sensor_height = float(self.sensor_height_var.get())
            average_road = float(self.average_road_var.get())

            if sensor_height < average_road:
                messagebox.showerror("Error", "Sensor height should be greater than or equal to average road height.")
                return

            hole_depth = sensor_height - average_road

            if self.unit_var.get() == 0:
                A_edge = sensor_height * math.tan(alpha_radians)
                Area = A_edge * A_edge
                Volume = Area * hole_depth
                asphalt_density = 2400  # kg/m3
                asphalt_weight = Volume * asphalt_density
            else:
                A_edge = sensor_height * math.tan(alpha_radians * 3.28084)
                Area = A_edge * A_edge * 10.7639
                Volume = Area * hole_depth * 35.3147
                asphalt_density = 94.6405
                asphalt_weight = Volume * asphalt_density

            result = {
                "Gamma": Gamma,
                "Hole Depth": hole_depth,
                "Area Width": A_edge,
                "Area": Area,
                "Volume": Volume,
                "Asphalt Weight": asphalt_weight
            }

            self.results.append(result)
            self.display_results(result)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")

    def display_results(self, result):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Gamma = {result['Gamma']} degrees\n"
                                   f"The depth of the hole is {result['Hole Depth']} "
                                   f"{self.get_unit_label('meter', 'foot')}\n"
                                   f"The width of the Area is {result['Area Width']} "
                                   f"{self.get_unit_label('meter', 'foot')}\n"
                                   f"The Area is: {result['Area']} "
                                   f"{self.get_unit_label('square meter', 'square foot')}\n"
                                   f"The volume is: {result['Volume']} "
                                   f"{self.get_unit_label('cubic meter', 'cubic foot')}\n"
                                   f"The asphalt weight needed is: {result['Asphalt Weight']} "
                                   f"{self.get_unit_label('kilogram', 'pound')}")

    def clear_result(self):
        self.result_text.delete(1.0, tk.END)

    def plot_2d_graph(self):
        try:
            sensor_height = float(self.sensor_height_var.get())
            average_road = float(self.average_road_var.get())
            hole_depth = sensor_height - average_road

            plt.figure()
            plt.plot(['Sensor Height', 'Average Road', 'Hole Depth'],
                     [sensor_height, average_road, hole_depth], marker='o', linestyle='-')
            plt.title("2D Graph")
            plt.ylabel(f"Depth ({self.get_unit_label('meter', 'foot')})")
            plt.grid(True)
            plt.show()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")

    def display_3d_visualization(self):
        try:
            sensor_height = float(self.sensor_height_var.get())
            average_road = float(self.average_road_var.get())
            hole_depth = sensor_height - average_road

            x = [hole_depth, -hole_depth, hole_depth, -hole_depth, hole_depth, -hole_depth, hole_depth, -hole_depth]
            y = [-hole_depth, hole_depth, hole_depth, -hole_depth, hole_depth, -hole_depth, -hole_depth, hole_depth]
            z = [hole_depth, hole_depth, hole_depth, hole_depth, average_road, average_road, average_road, average_road]

            triangles = [
                [0, 1, 2], [0, 2, 3],
                [4, 5, 6], [4, 6, 7],
                [0, 1, 5], [0, 5, 4],
                [2, 3, 7], [2, 7, 6],
                [0, 3, 7], [0, 7, 4],
                [1, 2, 6], [1, 6, 5]
            ]

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            ax.set_xlabel(f'X-axis ({self.get_unit_label("meter", "foot")})')
            ax.set_ylabel(f'Y-axis ({self.get_unit_label("meter", "foot")})')
            ax.set_zlabel(f'Z-axis ({self.get_unit_label("meter", "foot")})')
            plt.title("Data Coordination")

            colormap = cm.get_cmap('plasma')

            sc = ax.scatter(x, y, z, c=z, cmap=colormap, marker='o', s=50)

            cbar = fig.colorbar(sc)
            cbar.set_label(f'Depth ({self.get_unit_label("meter", "foot")})')

            ax.grid(True, linestyle='--', alpha=0.5)

            ax.xaxis.set_tick_params(labelsize=10)
            ax.yaxis.set_tick_params(labelsize=10)
            ax.zaxis.set_tick_params(labelsize=10)

            surf = ax.plot_trisurf(x, y, z, cmap=colormap, linewidth=1, antialiased=True, facecolors=colormap(z))

            surf.set_alpha(.5)

            plt.show()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")

    def display_video(self):
        try:
            if not self.sensor_angle_var.get() or not self.sensor_height_var.get() or not self.average_road_var.get():
                messagebox.showerror("Error", "Please enter all the required input values.")
                return

            sensor_angle = float(self.sensor_angle_var.get())
            sensor_height = float(self.sensor_height_var.get())
            average_road = float(self.average_road_var.get())

            if sensor_height < average_road:
                messagebox.showerror("Error", "Sensor height should be greater than or equal to average road height.")
                return

            self.cap = cv2.VideoCapture("B:/sagcg/fluid sim0001-0149.avi")

            if not self.cap.isOpened():
                messagebox.showerror("Error", "Unable to open the video file.")
                return

            self.video_label = tk.Label(self.root)
            self.video_label.pack()

            self.update_video()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for the input.")

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.video_label.config(image=photo)
            self.video_label.photo = photo
            self.video_label.after(10, self.update_video)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.update_video()

    def save_results(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(self.results, file)
            messagebox.showinfo("Success", f"Results saved to {file_path}")

    def export_visualization(self):
        try:
            sensor_height = float(self.sensor_height_var.get())
            average_road = float(self.average_road_var.get())
            hole_depth = sensor_height - average_road

            x = [hole_depth, -hole_depth, hole_depth, -hole_depth, hole_depth, -hole_depth, hole_depth, -hole_depth]
            y = [-hole_depth, hole_depth, hole_depth, -hole_depth, hole_depth, -hole_depth, -hole_depth, hole_depth]
            z = [hole_depth, hole_depth, hole_depth, hole_depth, average_road, average_road, average_road, average_road]

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            ax.set_xlabel(f'X-axis ({self.get_unit_label("meter", "foot")})')
            ax.set_ylabel(f'Y-axis ({self.get_unit_label("meter", "foot")})')
            ax.set_zlabel(f'Z-axis ({self.get_unit_label("meter", "foot")})')
            plt.title("Data Coordination")

            colormap = cm.get_cmap('plasma')

            sc = ax.scatter(x, y, z, c=z, cmap=colormap, marker='o', s=50)

            cbar = fig.colorbar(sc)
            cbar.set_label(f'Depth ({self.get_unit_label("meter", "foot")})')

            ax.grid(True, linestyle='--', alpha=0.5)

            ax.xaxis.set_tick_params(labelsize=10)
            ax.yaxis.set_tick_params(labelsize=10)
            ax.zaxis.set_tick_params(labelsize=10)

            export_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if export_path:
                plt.savefig(export_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Visualization saved to {export_path}")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")

    def generate_random_inputs(self):
        try:
            self.sensor_angle_var.set(round(random.uniform(0.1, 2.0), 2))
            self.sensor_height_var.set(round(random.uniform(0.5, 2.0), 2))
            self.average_road_var.set(round(random.uniform(0.5, min(float(self.sensor_height_var.get()), 2.0)), 2))
        except ValueError:
            messagebox.showerror("Error", "Failed to generate random inputs.")

    def get_unit_label(self, metric_label, imperial_label):
        return metric_label if self.unit_var.get() == 0 else imperial_label

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
