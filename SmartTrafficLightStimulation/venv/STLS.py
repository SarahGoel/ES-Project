import tkinter as tk
from tkinter import messagebox
import threading
import time
import os
import platform
import subprocess
import csv
from datetime import datetime

class TrafficLightApp: 
    def __init__(self, master): 
        self.master = master 
        self.master.title("Smart Traffic Light Control System") 
        self.master.geometry("600x700")

        self.directions = ["North", "East", "South", "West"]
        self.entries = {}
        self.signal_labels = {}
        self.pedestrian_labels = {}
        self.countdown_labels = {}
        self.running = False
        self.green_times = {}

        self.setup_ui()

    def setup_ui(self):
        # Frame for input fields
        input_frame = tk.Frame(self.master)
        input_frame.pack(pady=10)

        for direction in self.directions:
             frame = tk.Frame(input_frame)
             frame.pack(pady=5)

             label = tk.Label(frame, text=f"{direction} Vehicles:")
             label.pack(side="left")

             entry = tk.Entry(frame, width=5)
             entry.pack(side="left")
             self.entries[direction] = entry

        self.start_button = tk.Button(self.master, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack(pady=10)

        # Traffic and pedestrian signal labels
        self.signal_frame = tk.Frame(self.master)
        self.signal_frame.pack(pady=10)

        for direction in self.directions:
            frame = tk.Frame(self.signal_frame, borderwidth=2, relief="groove", padx=10, pady=5)
            frame.pack(pady=5)

            signal = tk.Label(frame, text=f"{direction} Light: RED", width=30)
            signal.pack()
            self.signal_labels[direction] = signal

            ped = tk.Label(frame, text="Pedestrian Signal: WALK", fg="green")
            ped.pack()
            self.pedestrian_labels[direction] = ped

            countdown = tk.Label(frame, text="")
            countdown.pack()
            self.countdown_labels[direction] = countdown

        # Log Frame
        self.log_frame = tk.Frame(self.master)
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        log_label = tk.Label(self.log_frame, text="Simulation Log", font=("Arial", 12, "bold"))
        log_label.pack(anchor="w")

        # Filter dropdown
        filter_frame = tk.Frame(self.log_frame)
        filter_frame.pack(anchor="e", pady=5)

        tk.Label(filter_frame, text="Filter:").pack(side="left")
        self.filter_var = tk.StringVar()
        self.filter_var.set("All")
        options = ["All"] + self.directions
        filter_menu = tk.OptionMenu(filter_frame, self.filter_var, *options, command=self.update_log_preview)
        filter_menu.pack(side="left")

        self.log_text = tk.Text(self.log_frame, height=10, wrap="word")
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Buttons below log
        log_btn_frame = tk.Frame(self.master)
        log_btn_frame.pack(pady=5)

        clear_btn = tk.Button(log_btn_frame, text="Clear Logs", command=self.clear_log_preview)
        clear_btn.pack(side="left", padx=10)

        open_btn = tk.Button(log_btn_frame, text="Open Log Folder", command=self.open_log_folder)
        open_btn.pack(side="left", padx=10)

    def start_simulation(self):
        if self.running:
            return

        try:
            vehicle_data = {dir: int(self.entries[dir].get()) for dir in self.directions}
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for all directions.")
            return

        self.green_times = self.calculate_green_times(vehicle_data)
        self.init_logging()
        self.running = True
        self.start_button.config(state="disabled")
        threading.Thread(target=self.run_simulation).start()

    def calculate_green_times(self, vehicle_data):
        max_time = 30
        total = sum(vehicle_data.values())
        return {
            dir: max(5, int((vehicle_data[dir] / total) * max_time)) if total > 0 else 10
            for dir in vehicle_data
        }

    def update_signals(self, green_dir, traffic_color, ped_signal):
        for dir in self.directions:
            color = traffic_color if dir == green_dir else "RED"
            self.signal_labels[dir].config(text=f"{dir} Light: {color}", fg="green" if color == "GREEN" else "red")
            self.pedestrian_labels[dir].config(text="Pedestrian Signal: WALK" if color == "RED" else "Pedestrian Signal: DON'T WALK", fg="green" if color == "RED" else "red")

    def run_simulation(self):
        for direction in sorted(self.green_times, key=self.green_times.get, reverse=True):
            duration = self.green_times[direction]
            vehicle_count = int(self.entries[direction].get())
            timestamp = datetime.now().strftime("%H:%M:%S")

            self.log_data.append({
                "Time": timestamp,
                "Direction": direction,
                "Vehicles": vehicle_count,
                "Green_Time": duration
            })

            self.update_signals(direction, "GREEN", "DON'T WALK")
            for i in range(duration, 0, -1):
                self.countdown_labels[direction].config(text=f"{i} seconds remaining")
                time.sleep(1)
            self.update_signals(direction, "RED", "WALK")
            self.countdown_labels[direction].config(text="")
            time.sleep(3)

        self.save_logs()
        self.update_log_preview()
        self.running = False
        self.start_button.config(state="normal")

    def init_logging(self):
        self.log_data = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_filename_txt = f"log_{self.timestamp}.txt"
        self.log_filename_csv = f"log_{self.timestamp}.csv"

    def save_logs(self):
        with open(self.log_filename_txt, "w") as f:
            f.write(f"Smart Traffic Log - {self.timestamp}\n\n")
            for entry in self.log_data:
                line = f"[{entry['Time']}] {entry['Direction']} - Vehicles: {entry['Vehicles']} | Green Time: {entry['Green_Time']}s\n"
                f.write(line)

        with open(self.log_filename_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Time", "Direction", "Vehicles", "Green_Time"])
            writer.writeheader()
            writer.writerows(self.log_data)

    def update_log_preview(self, *_):
        self.log_text.delete("1.0", tk.END)
        selected_filter = self.filter_var.get()

        for entry in self.log_data:
            if selected_filter != "All" and entry["Direction"] != selected_filter:
                continue
            line = f"[{entry['Time']}] {entry['Direction']} - Vehicles: {entry['Vehicles']} | Green Time: {entry['Green_Time']}s\n"
            self.log_text.insert(tk.END, line)

            index = self.log_text.index("insert")
            line_start = f"{float(index.split('.')[0]) - 1}.0"

            self.log_text.tag_add("timestamp", line_start, f"{line_start}+9c")
            self.log_text.tag_add("direction", f"{line_start}+11c", f"{line_start}+11c+{len(entry['Direction'])}c")
            self.log_text.tag_add("green", f"{line_start} lineend-10c", f"{line_start} lineend")

        self.log_text.tag_config("timestamp", foreground="gray")
        self.log_text.tag_config("direction", foreground="black", font=("Arial", 10, "bold"))
        self.log_text.tag_config("green", foreground="blue", font=("Arial", 10, "italic"))

    def clear_log_preview(self):
        self.log_text.delete("1.0", tk.END)

    def open_log_folder(self):
        folder_path = os.getcwd()
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")

if __name__ == "__main__": 
    root = tk.Tk()
    app = TrafficLightApp(root) 
    root.mainloop()