import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import math
import time
import os
import json
import threading
from PIL import Image, ImageTk, ImageDraw
import pygame
import sys

WHEEL_DIR = "wheels"
SOUND_DIR = "sounds"

class SpinTheWheel:
    def __init__(self, wheel_name, items_with_sizes, parent_manager=None):
        self.wheel_name = wheel_name
        self.items_with_sizes = items_with_sizes
        self.total = sum(size for _, size in items_with_sizes)
        self.angle_per_unit = 360 / self.total
        self.rotation = 0
        self.is_spinning = False
        self.parent_manager = parent_manager

        # Make independent window
        self.root = tk.Toplevel()
        self.root.title(f"Spin the Wheel - {wheel_name}")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"600x700+{x}+{y}")

        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text=f"Spin the Wheel - {wheel_name}",
                font=("Arial", 18, "bold"), fg="white", bg="#2c3e50").pack(expand=True)

        # Canvas for wheel
        self.canvas = tk.Canvas(self.root, width=500, height=500, bg="white", highlightthickness=0)
        self.canvas.pack(pady=20)

        # Result display
        result_frame = tk.Frame(self.root, bg="#f0f0f0")
        result_frame.pack(fill=tk.X, pady=(0, 10))

        self.result_var = tk.StringVar()
        self.result_label = tk.Label(result_frame, textvariable=self.result_var,
                                    font=("Arial", 16, "bold"), fg="#e74c3c", bg="#f0f0f0")
        self.result_label.pack()

        # Button frame
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=10)

        self.spin_button = tk.Button(button_frame, text="SPIN", command=self.spin,
                                    font=("Arial", 14, "bold"), bg="#3498db", fg="white",
                                    width=10, height=2, relief="flat", cursor="hand2")
        self.spin_button.pack(side=tk.LEFT, padx=5)

        # Add Edit button if we have a parent manager
        if self.parent_manager:
            self.edit_button = tk.Button(button_frame, text="EDIT", command=self.edit_wheel,
                                       font=("Arial", 14), bg="#f39c12", fg="white",
                                       width=10, height=2, relief="flat", cursor="hand2")
            self.edit_button.pack(side=tk.LEFT, padx=5)

        self.close_button = tk.Button(button_frame, text="CLOSE", command=self.root.destroy,
                                     font=("Arial", 14), bg="#95a5a6", fg="white",
                                     width=10, height=2, relief="flat", cursor="hand2")
        self.close_button.pack(side=tk.LEFT, padx=5)

        # Initialize sound
        self.init_sound()

        # Draw the wheel
        self.draw_wheel()

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Center the window on screen
        self.center_window()

    def init_sound(self):
        """Initialize sound system"""
        try:
            pygame.mixer.init()
            self.spin_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "spin.wav")) if os.path.exists(SOUND_DIR) else None
            self.win_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "win.wav")) if os.path.exists(SOUND_DIR) else None
        except:
            self.spin_sound = None
            self.win_sound = None

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")

    def draw_wheel(self):
        """Draw the wheel with items"""
        self.canvas.delete("all")
        radius = 200
        center = (250, 250)
        colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c",
                 "#d35400", "#c0392b", "#16a085", "#8e44ad", "#2c3e50", "#f1c40f"]

        # Draw wheel shadow
        shadow_offset = 4
        self.canvas.create_oval(center[0]-radius+shadow_offset, center[1]-radius+shadow_offset,
                               center[0]+radius+shadow_offset, center[1]+radius+shadow_offset,
                               fill="#888888", outline="")

        # Draw wheel
        start_angle = self.rotation
        for i, (item, size) in enumerate(self.items_with_sizes):
            extent = size * self.angle_per_unit
            color = colors[i % len(colors)]

            # Draw segment
            self.canvas.create_arc(
                center[0]-radius, center[1]-radius,
                center[0]+radius, center[1]+radius,
                start=start_angle, extent=extent,
                fill=color, outline="white", width=2
            )

            # Text
            angle_rad = math.radians(start_angle + extent/2)
            text_radius = radius * 0.75  # Position text closer to center
            x = center[0] + text_radius * math.cos(angle_rad)
            y = center[1] - text_radius * math.sin(angle_rad)

            # Adjust text orientation
            text_angle = start_angle + extent/2
            if text_angle > 90 and text_angle < 270:
                text_angle += 180

            self.canvas.create_text(x, y, text=item, font=("Arial", 10, "bold"),
                                   angle=text_angle, fill="white")

            start_angle += extent

        # Draw center circle
        self.canvas.create_oval(center[0]-20, center[1]-20,
                               center[0]+20, center[1]+20,
                               fill="#2c3e50", outline="white", width=2)

        # Draw pointer
        pointer_points = [240, 20, 260, 20, 250, 0]
        self.canvas.create_polygon(pointer_points, fill="#e74c3c", outline="black", width=2)

        # Draw pointer stand
        self.canvas.create_rectangle(245, 20, 255, 40, fill="#7f8c8d", outline="black", width=1)

    def spin(self):
        """Start the spinning animation"""
        if self.is_spinning:
            return

        self.is_spinning = True
        self.spin_button.config(state=tk.DISABLED)
        if hasattr(self, 'edit_button'):
            self.edit_button.config(state=tk.DISABLED)
        self.result_var.set("Spinning...")

        # Play spin sound if available
        if self.spin_sound:
            self.spin_sound.play()

        # Determine spin parameters
        spins = random.randint(5, 8)  # Number of full rotations
        total_degrees = spins * 360 + random.randint(0, 359)
        duration = 4.0  # seconds
        steps = int(duration * 30)  # 30 FPS
        step_degrees = total_degrees / steps

        # Easing function for more realistic spin
        def ease_out_quad(t):
            return t * (2 - t)

        # Animate the spin
        start_time = time.time()

        def animate():
            if not self.is_spinning:
                return

            elapsed = time.time() - start_time
            if elapsed > duration:
                self.finish_spin(total_degrees % 360)
                return

            # Calculate rotation with easing
            progress = elapsed / duration
            eased_progress = ease_out_quad(progress)
            current_rotation = eased_progress * total_degrees

            self.rotation = current_rotation % 360
            self.draw_wheel()

            # Schedule next frame
            self.root.after(33, animate)  # ~30 FPS

        animate()

    def finish_spin(self, final_rotation):
        """Finish spinning and determine winner"""
        self.rotation = final_rotation
        self.draw_wheel()

        # Determine winner
        angle = (360 - self.rotation) % 360
        total_angle = 0
        winner = None

        for item, size in self.items_with_sizes:
            extent = size * self.angle_per_unit
            if total_angle <= angle < total_angle + extent:
                winner = item
                break
            total_angle += extent

        # Display result
        if winner:
            self.result_var.set(f"🎉 Winner: {winner} 🎉")

            # Play win sound if available
            if self.win_sound:
                self.win_sound.play()

        self.is_spinning = False
        self.spin_button.config(state=tk.NORMAL)
        if hasattr(self, 'edit_button'):
            self.edit_button.config(state=tk.NORMAL)

    def edit_wheel(self):
        """Edit the current wheel"""
        if self.is_spinning:
            return

        # Open edit dialog with existing data
        edit_dialog = WheelDialog(self.root, "Edit Wheel", self.wheel_name, self.items_with_sizes)
        self.root.wait_window(edit_dialog.top)

        if edit_dialog.result:
            new_name, items = edit_dialog.result
            if new_name and items:
                # Update the wheel with new data
                self.wheel_name = new_name
                self.items_with_sizes = items
                self.total = sum(size for _, size in items)
                self.angle_per_unit = 360 / self.total

                # Update window title
                self.root.title(f"Spin the Wheel - {self.wheel_name}")

                # Redraw the wheel
                self.draw_wheel()

                # Save the changes
                save_wheel(self.wheel_name, self.items_with_sizes)

                # Show success message
                self.result_var.set(f"Wheel updated: {self.wheel_name}")

    def on_close(self):
        """Handle window closing"""
        self.is_spinning = False
        self.root.destroy()


# ===========================
# Wheel Manager
# ===========================
def ensure_wheel_dir():
    if not os.path.exists(WHEEL_DIR):
        os.makedirs(WHEEL_DIR)

def ensure_sound_dir():
    if not os.path.exists(SOUND_DIR):
        os.makedirs(SOUND_DIR)
        print(f"Created {SOUND_DIR} directory. Add spin.wav and win.wav files for sound effects.")

def list_wheels():
    ensure_wheel_dir()
    return [f.replace(".json", "") for f in os.listdir(WHEEL_DIR) if f.endswith(".json")]

def save_wheel(name, items_with_sizes):
    ensure_wheel_dir()
    path = os.path.join(WHEEL_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(items_with_sizes, f)
    print(f"✅ Wheel '{name}' saved.")

def load_wheel(name):
    path = os.path.join(WHEEL_DIR, f"{name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def delete_wheel(name):
    path = os.path.join(WHEEL_DIR, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
        print(f"🗑️ Wheel '{name}' deleted.")


# ===========================
# GUI Menu
# ===========================
class WheelManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Spin The Wheel Manager")
        self.root.geometry("600x550")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)

        # Center the window
        self.center_window()

        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="🎡 Spin The Wheel Manager 🎡",
                font=("Arial", 20, "bold"), fg="white", bg="#2c3e50").pack(expand=True)

        # Main content
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Buttons
        button_style = {"font": ("Arial", 14), "width": 20, "height": 2,
                       "relief": "flat", "cursor": "hand2"}

        tk.Button(main_frame, text="Create New Wheel", command=self.create_wheel,
                 bg="#3498db", fg="white", **button_style).pack(pady=10)

        tk.Button(main_frame, text="Load Existing Wheel", command=self.load_wheel,
                 bg="#2ecc71", fg="white", **button_style).pack(pady=10)

        tk.Button(main_frame, text="Edit Wheel", command=self.edit_wheel,
                 bg="#f39c12", fg="white", **button_style).pack(pady=10)

        tk.Button(main_frame, text="Delete Wheel", command=self.delete_wheel,
                 bg="#e74c3c", fg="white", **button_style).pack(pady=10)

        tk.Button(main_frame, text="Exit", command=self.root.quit,
                 bg="#95a5a6", fg="white", **button_style).pack(pady=10)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                             font=("Arial", 10), bg="#bdc3c7", fg="#2c3e50", relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Initialize directories
        ensure_wheel_dir()
        ensure_sound_dir()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (550 // 2)
        self.root.geometry(f"600x550+{x}+{y}")

    def create_wheel(self):
        """Create a new wheel"""
        dialog = WheelDialog(self.root, "Create New Wheel")
        self.root.wait_window(dialog.top)

        if dialog.result:
            name, items = dialog.result
            if name and items:
                save_wheel(name, items)
                SpinTheWheel(name, items, self)  # Pass self as parent_manager
                self.status_var.set(f"Created wheel: {name}")

    def load_wheel(self):
        """Load an existing wheel"""
        wheels = list_wheels()
        if not wheels:
            messagebox.showinfo("No Wheels", "No wheels saved yet.")
            return

        dialog = WheelSelector(self.root, wheels, "Select Wheel to Load")
        self.root.wait_window(dialog.top)

        if dialog.selected:
            name = dialog.selected
            data = load_wheel(name)
            if data:
                SpinTheWheel(name, data, self)  # Pass self as parent_manager
                self.status_var.set(f"Loaded wheel: {name}")

    def edit_wheel(self):
        """Edit an existing wheel"""
        wheels = list_wheels()
        if not wheels:
            messagebox.showinfo("No Wheels", "No wheels saved yet.")
            return

        dialog = WheelSelector(self.root, wheels, "Select Wheel to Edit")
        self.root.wait_window(dialog.top)

        if dialog.selected:
            name = dialog.selected
            data = load_wheel(name)
            if data:
                # Open edit dialog with existing data
                edit_dialog = WheelDialog(self.root, "Edit Wheel", name, data)
                self.root.wait_window(edit_dialog.top)

                if edit_dialog.result:
                    new_name, items = edit_dialog.result
                    if new_name and items:
                        # If name changed, delete old file
                        if new_name != name:
                            delete_wheel(name)
                        save_wheel(new_name, items)
                        self.status_var.set(f"Updated wheel: {new_name}")
                        messagebox.showinfo("Success", f"Wheel '{new_name}' has been updated.")

    def delete_wheel(self):
        """Delete a wheel"""
        wheels = list_wheels()
        if not wheels:
            messagebox.showinfo("No Wheels", "No wheels saved yet.")
            return

        dialog = WheelSelector(self.root, wheels, "Select Wheel to Delete")
        self.root.wait_window(dialog.top)

        if dialog.selected:
            name = dialog.selected
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
                delete_wheel(name)
                self.status_var.set(f"Deleted wheel: {name}")
                messagebox.showinfo("Deleted", f"Wheel '{name}' has been deleted.")


class WheelDialog:
    """Dialog for creating or editing a wheel"""
    def __init__(self, parent, title, existing_name=None, existing_items=None):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("500x450")
        self.top.configure(bg="#f0f0f0")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        # Center the dialog
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.top.winfo_screenheight() // 2) - (450 // 2)
        self.top.geometry(f"500x450+{x}+{y}")

        self.result = None

        # Wheel name
        tk.Label(self.top, text="Wheel Name:", font=("Arial", 12), bg="#f0f0f0").pack(pady=(20, 5))
        self.name_var = tk.StringVar(value=existing_name if existing_name else "")
        name_entry = tk.Entry(self.top, textvariable=self.name_var, font=("Arial", 12), width=30)
        name_entry.pack(pady=(0, 20))

        # Items frame
        tk.Label(self.top, text="Items (one per line, format: name or name:size):",
                font=("Arial", 12), bg="#f0f0f0").pack(pady=(0, 5))

        frame = tk.Frame(self.top, bg="#f0f0f0")
        frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.items_text = tk.Text(frame, font=("Arial", 11), width=40, height=12)
        scrollbar = tk.Scrollbar(frame, command=self.items_text.yview)
        self.items_text.configure(yscrollcommand=scrollbar.set)

        self.items_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # If editing, populate with existing items
        if existing_items:
            items_text = ""
            for item, size in existing_items:
                if size == 1:
                    items_text += f"{item}\n"
                else:
                    items_text += f"{item}:{size}\n"
            self.items_text.insert(tk.END, items_text.strip())
        else:
            # Example text for new wheels
            self.items_text.insert(tk.END, "Apple\nBanana:3\nOrange\nGrapes:2")

        # Buttons
        button_frame = tk.Frame(self.top, bg="#f0f0f0")
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="OK", command=self.ok,
                 font=("Arial", 12), width=10, bg="#2ecc71", fg="white").pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Cancel", command=self.cancel,
                 font=("Arial", 12), width=10, bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=10)

        # Set focus to name entry
        name_entry.focus()

    def ok(self):
        """Handle OK button"""
        name = self.name_var.get().strip()
        items_text = self.items_text.get("1.0", tk.END).strip()

        if not name:
            messagebox.showerror("Error", "Please enter a wheel name.")
            return

        if not items_text:
            messagebox.showerror("Error", "Please enter at least one item.")
            return

        items_with_sizes = []
        for line in items_text.split("\n"):
            line = line.strip()
            if not line:
                continue

            if ":" in line:
                parts = line.split(":", 1)
                item = parts[0].strip()
                try:
                    size = int(parts[1].strip())
                    if size <= 0:
                        raise ValueError
                    items_with_sizes.append((item, size))
                except ValueError:
                    messagebox.showerror("Error", f"Invalid size for '{item}'. Size must be a positive integer.")
                    return
            else:
                # Default size is 1 if not specified
                items_with_sizes.append((line, 1))

        if len(items_with_sizes) < 2:
            messagebox.showerror("Error", "Need at least 2 items.")
            return

        self.result = (name, items_with_sizes)
        self.top.destroy()

    def cancel(self):
        """Handle Cancel button"""
        self.top.destroy()


class WheelSelector:
    """Dialog for selecting a wheel"""
    def __init__(self, parent, wheels, title):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("400x300")
        self.top.configure(bg="#f0f0f0")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        # Center the dialog
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.top.winfo_screenheight() // 2) - (300 // 2)
        self.top.geometry(f"400x300+{x}+{y}")

        self.selected = None

        tk.Label(self.top, text="Select a wheel:", font=("Arial", 12), bg="#f0f0f0").pack(pady=20)

        frame = tk.Frame(self.top, bg="#f0f0f0")
        frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.listbox = tk.Listbox(frame, font=("Arial", 12), selectmode=tk.SINGLE)
        scrollbar = tk.Scrollbar(frame, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)

        for wheel in wheels:
            self.listbox.insert(tk.END, wheel)

        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        button_frame = tk.Frame(self.top, bg="#f0f0f0")
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Select", command=self.select,
                 font=("Arial", 12), width=10, bg="#3498db", fg="white").pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Cancel", command=self.cancel,
                 font=("Arial", 12), width=10, bg="#95a5a6", fg="white").pack(side=tk.LEFT, padx=10)

        # Bind double-click
        self.listbox.bind("<Double-Button-1>", lambda e: self.select())

    def select(self):
        """Handle selection"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a wheel.")
            return

        self.selected = self.listbox.get(selection[0])
        self.top.destroy()

    def cancel(self):
        """Handle cancel"""
        self.top.destroy()


if __name__ == "__main__":
    # Create main window
    root = tk.Tk()
    app = WheelManager(root)
    root.mainloop()
