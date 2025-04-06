import copy
import tkinter as tk
import yaml
from PIL import Image, ImageTk, ImageDraw
import os


class PointOrBoxDialog:
    def __init__(self, root, item_type, event, on_save_callback):
        self.root = root
        self.item_type = item_type
        self.event = event
        self.on_save_callback = on_save_callback

        self.dialog = tk.Toplevel(self.root)
        self.dialog.title(f"Enter {self.item_type} Info")
        self.dialog.geometry("300x300")  # Set a fixed size for the dialog

        self.center_dialog()

        # Frame for organizing the fields
        self.form_frame = tk.Frame(self.dialog)
        self.form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Add Name field
        self.name_label = tk.Label(self.form_frame, text="Enter name:")
        self.name_label.grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(self.form_frame)
        self.name_entry.grid(row=0, column=1, pady=5, sticky="ew")
        self.form_frame.grid_columnconfigure(1, weight=1)

        # Add Location section
        self.location_label = tk.Label(self.form_frame, text="Select location:")
        self.location_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

        self.location_var = tk.StringVar(self.dialog)
        self.location_var.set("center")  # Default value

        # Create location buttons with arrows
        self.arrow_frame = tk.Frame(self.form_frame)
        self.arrow_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.create_location_buttons()

        # Save button
        self.save_button = tk.Button(
            self.dialog, text="Save", command=self.on_save, width=20
        )
        self.save_button.pack(pady=10)

        # Bind keyboard events
        self.dialog.bind(
            "<KeyPress-Up>", lambda event: self.on_location_click("top", self.up_button)
        )
        self.dialog.bind(
            "<KeyPress-Left>",
            lambda event: self.on_location_click("left", self.left_button),
        )
        self.dialog.bind(
            "<KeyPress-Right>",
            lambda event: self.on_location_click("right", self.right_button),
        )
        self.dialog.bind(
            "<KeyPress-Down>",
            lambda event: self.on_location_click("bottom", self.down_button),
        )

        self.dialog.bind("<Return>", lambda event: self.on_save())  # Save on Enter
        self.dialog.bind(
            "<Escape>", lambda event: self.on_discard()
        )  # Discard on Escape

        # Make sure dialog is on top and active
        self.dialog.transient(self.root)
        self.dialog.grab_set()  # Capture all events for this dialog
        self.dialog.focus_set()  # Set focus to the dialog
        self.dialog.lift()  # Bring the dialog to the top of the window stack

        self.name_entry.focus_set()  # Focus the Name entry field

        # Wait until the dialog is closed
        self.root.wait_window(self.dialog)

    def center_dialog(self):
        # Get the dimensions of the parent window (root)
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()

        # Get the dimensions of the dialog
        dialog_width = 300  # Fixed width of the dialog
        dialog_height = 300  # Fixed height of the dialog

        # Calculate the position to center the dialog on the parent window
        x_position = root_x + (root_width // 2) - (dialog_width // 2)
        y_position = root_y + (root_height // 2) - (dialog_height // 2)

        # Set the geometry of the dialog
        self.dialog.geometry(
            f"{dialog_width}x{dialog_height}+{x_position}+{y_position}"
        )

    def create_location_buttons(self):
        button_style = {"font": ("Arial", 18), "width": 3}

        self.up_button = tk.Button(
            self.arrow_frame,
            text="↑",
            command=lambda: self.on_location_click("top", self.up_button),
            **button_style,
        )
        self.up_button.grid(row=0, column=1)

        self.left_button = tk.Button(
            self.arrow_frame,
            text="←",
            command=lambda: self.on_location_click("left", self.left_button),
            **button_style,
        )
        self.left_button.grid(row=1, column=0)

        self.right_button = tk.Button(
            self.arrow_frame,
            text="→",
            command=lambda: self.on_location_click("right", self.right_button),
            **button_style,
        )
        self.right_button.grid(row=1, column=2)

        self.down_button = tk.Button(
            self.arrow_frame,
            text="↓",
            command=lambda: self.on_location_click("bottom", self.down_button),
            **button_style,
        )
        self.down_button.grid(row=2, column=1)

        self.center_button = tk.Button(
            self.arrow_frame,
            text=" ",
            command=lambda: self.on_location_click("center", self.center_button),
            **button_style,
        )
        self.center_button.grid(row=1, column=1)

        self.on_location_click('center', self.center_button)

    def on_location_click(self, location, button):
        self.location_var.set(location)
        # Reset background color of all buttons
        for btn in [
            self.up_button,
            self.left_button,
            self.right_button,
            self.down_button,
            self.center_button,
        ]:
            btn.config(bg="SystemButtonFace")  # Default color
        # Highlight selected button
        button.config(bg="lightblue")  # Highlight color

    def on_save(self):
        name = self.name_entry.get()
        location = self.location_var.get()

        # Trigger the callback to save the point or box
        self.on_save_callback(name, location)

        self.dialog.destroy()  # Close dialog after saving

    def on_discard(self):
        # Close dialog without saving (discard changes)
        self.dialog.destroy()


class BoundingBoxApp:
    def __init__(self, root, image_path, image_output_path="output.png", yaml_path='annotations_test.yaml'):
        self.image_output_path = image_output_path

        self.root = root
        self.root.title("Bounding Box Drawer")

        self.image_path = image_path
        self.image = Image.open(image_path)
        self.image_width, self.image_height = self.image.size

        self.canvas = tk.Canvas(
            self.root, width=self.image_width, height=self.image_height
        )
        self.canvas.pack(side=tk.BOTTOM)

        # Toolbar frame
        self.toolbar_frame = tk.Frame(self.root)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        # Buttons to select mode
        self.point_button = tk.Button(
            self.toolbar_frame, text="Draw Point", command=self.set_point_mode
        )
        self.point_button.pack(side=tk.LEFT, padx=5)

        self.box_button = tk.Button(
            self.toolbar_frame, text="Draw Bounding Box", command=self.set_box_mode
        )
        self.box_button.pack(side=tk.LEFT, padx=5)

        self.current_mode = "point"  # Default mode is "point"
        self.update_toolbar()

        self.bounding_boxes = []
        self.points = []
        self.current_item = None
        self.drag_start_x = None
        self.drag_start_y = None

        # Load existing data if available
        self.data_file = yaml_path
        self.load_data()

        self.display_image()

        self.canvas.focus_set()  # Set focus on the canvas

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<KeyPress-q>", self.close)

    def display_image(self):
        # Convert the image to a Tkinter-compatible photo image
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        # Draw existing bounding boxes and points
        for item in self.bounding_boxes:
            self.draw_bounding_box(item)
        for point in self.points:
            self.draw_point(point)

    def draw_bounding_box(self, box):
        text = f"{box['name']} ({box['location']})"
        color = "red"
        width = 2

        # Draw on Image
        draw = ImageDraw.Draw(self.image)
        draw.rectangle(
            [box["x1"], box["y1"], box["x2"], box["y2"]], outline=color, width=width
        )
        draw.text(
            ((box["x1"] + box["x2"]) // 2, box["y1"] - 10), text=text, fill=color
        )
        
        # Draw on Convas
        self.canvas.create_rectangle(
            box["x1"], box["y1"], box["x2"], box["y2"], outline=color, width=width
        )
        self.canvas.create_text(
            (box["x1"] + box["x2"]) // 2, box["y1"] - 10, text=text, fill=color
        )

    def draw_point(self, point):
        text = f"{point['name']} ({point['location']})"
        color = "blue"
        width = 5

        # Draw on Image
        draw = ImageDraw.Draw(self.image)
        draw.ellipse(
            [point["x"] - width, point["y"] - width, point["x"] + width, point["y"] + width],
            outline=color,
            fill=color,
        )
        # Optional: Draw the label text on the image as well (same as canvas)
        draw.text((point["x"], point["y"] - 10), text=text, fill=color)

        # Draw on Canvas
        self.canvas.create_oval(
            point["x"] - width,
            point["y"] - width,
            point["x"] + width,
            point["y"] + width,
            outline=color,
            fill=color,
        )
        self.canvas.create_text(
            point["x"], point["y"] - 10, text=text, fill=color
        )

    def set_point_mode(self):
        self.current_mode = "point"
        self.update_toolbar()

    def set_box_mode(self):
        self.current_mode = "box"
        self.update_toolbar()

    def update_toolbar(self):
        # Update toolbar to visually indicate selected tool
        if self.current_mode == "point":
            self.point_button.config(bg="lightblue")
            self.box_button.config(bg="SystemButtonFace")
        elif self.current_mode == "box":
            self.box_button.config(bg="lightblue")
            self.point_button.config(bg="SystemButtonFace")

    def on_click(self, event):
        # Only prompt for a name if the user is in point or box mode
        if self.current_mode == "point":
            self.create_point(event)
        elif self.current_mode == "box":
            # Start defining a bounding box (do not show prompt yet)
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.current_item = {
                "x1": self.drag_start_x,
                "y1": self.drag_start_y,
                "x2": self.drag_start_x,
                "y2": self.drag_start_y,
            }

    def create_point(self, event):
        # Finish defining the bounding box
        self.show_point_or_box_dialog(
            "point", event
        )  # Trigger the dialog after release

        self.current_item = None  # Reset after bounding box is defined

    def on_drag(self, event):
        # If there's an active bounding box being dragged, update its position
        if self.current_item:
            # Update the current bounding box dimensions while dragging
            self.current_item["x2"] = event.x
            self.current_item["y2"] = event.y
            self.redraw_current_bounding_box()

    def redraw_current_bounding_box(self):
        self.canvas.delete("temp_box")  # Clear temporary bounding box being dragged
        self.canvas.create_rectangle(
            self.current_item["x1"],
            self.current_item["y1"],
            self.current_item["x2"],
            self.current_item["y2"],
            outline="green",
            width=2,
            tags="temp_box",
        )

    def show_point_or_box_dialog(self, item_type, event):
        def on_save(name, location):
            if item_type == "point":
                # Create point and add it to the list
                x, y = event.x, event.y
                # x /= self.image_width
                # y /= self.image_height
                point = {"name": name, "x": x, "y": y, "location": location}
                self.points.append(point)
                self.draw_point(point)
            elif item_type == "box":
                # Create bounding box and add it to the list
                x1, y1, x2, y2 = (
                    self.current_item["x1"],
                    self.current_item["y1"],
                    self.current_item["x2"],
                    self.current_item["y2"],
                )
                # x1 /= self.image_width
                # x2 /= self.image_width
                # y1 /= self.image_height
                # y2 /= self.image_height
                box = {
                    "name": name,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "location": location,
                }
                self.bounding_boxes.append(box)
                self.draw_bounding_box(box)

            self.save_data()

        # Create and display the dialog
        PointOrBoxDialog(self.root, item_type, event, on_save)

    def on_release(self, event):
        # Finish defining the bounding box
        if self.current_item:
            self.show_point_or_box_dialog(
                "box", event
            )  # Trigger the dialog after release

            self.current_item = None  # Reset after bounding box is defined

    def save_data(self):
        # Save bounding boxes and points to YAML file
        bounding_boxes, points = self.normalise_data()
        positions = {
            **{bbox["name"]: {**bbox, "location_type": "BoundingBox"} for bbox in bounding_boxes},
            **{pt["name"]: {**pt, "location_type": "Point"} for pt in points}
        }

        data = {
            "size": {"width": self.image_width, "height": self.image_height},
            "positions": {"test": positions},
            # "bounding_boxes": bounding_boxes,
            # "points": points,
        }
        with open(self.data_file, "w") as file:
            yaml.dump(data, file)

        if self.image_output_path is not None:
            self.image.save(self.image_output_path)

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
                positions = data.get("positions", {})
                positions = positions.get("test", {})
                for name, d in positions.items():
                    if d["location_type"] == "Point":
                        self.points.append(d)
                    elif d["location_type"] == "BoundingBox":
                        self.bounding_boxes.append(d)

                # self.bounding_boxes = data.get("bounding_boxes", [])
                # self.points = data.get("points", [])
        else:
            self.bounding_boxes = []
            self.points = []

        self.unnormalise_data()

    def unnormalise_data(self):
        for d in self.bounding_boxes:
            d["x1"] *= self.image_width
            d["x2"] *= self.image_width
            d["y1"] *= self.image_height
            d["y2"] *= self.image_height
        for d in self.points:
            d["x"] *= self.image_width
            d["y"] *= self.image_height

    def normalise_data(self):
        bounding_boxes = copy.deepcopy(self.bounding_boxes)
        points = copy.deepcopy(self.points)
        for d in bounding_boxes:
            d["x1"] /= self.image_width
            d["x2"] /= self.image_width
            d["y1"] /= self.image_height
            d["y2"] /= self.image_height
        for d in points:
            d["x"] /= self.image_width
            d["y"] /= self.image_height
        return bounding_boxes, points
    
    def close(self, event):
        self.root.destroy()

def main():
    root = tk.Tk()
    app = BoundingBoxApp(root, "temp/annotations/1/input.png")  # Provide your image file here
    root.mainloop()

def annotate(**params):
    root = tk.Tk()
    app = BoundingBoxApp(root, **params)  # Provide your image file here
    root.mainloop()


if __name__ == "__main__":
    main()
