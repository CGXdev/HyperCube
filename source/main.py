from panda3d.core import NodePath, LColor, Point3, WindowProperties
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class _3DStage(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()

        logger.debug('Initializing HyperCube')

        # Load the move sound
        self.move_sound = self.loader.loadSfx("move.wav")
        logger.info('Move sound loaded.')

        # Set the window title
        props = WindowProperties()
        props.setTitle("HyperCube")
        self.win.requestProperties(props)
        logger.info('Set window title')

        # Set initial camera position and orientation
        self.reset_camera()

        # Store multiple objects
        self.objects = []

        # Create a default cube object
        self.create_new_object()  # Create a default object

        self.keyMap = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "vup": False,
            "vdown": False
        }

        self.movement_step = 1  # Amount to move per button press (e.g., 1 unit)
        self.vertical_step = 1  # Amount to move up/down per button press (e.g., 1 unit)
        self.taskMgr.add(self.move_camera_task, "MoveCameraTask")

    def reset_camera(self):
        self.camera.setPos(0, -10, 0)  # Position the camera at (0, -10, 0)
        self.camera.lookAt(Point3(0, 0, 0))  # Look at the origin
        self.camera.setHpr(0, 0, 0)  # Reset Heading, Pitch, and Roll
        logger.info('Camera reset to position (0, -10, 0).')

    def create_object_model(self, model_path):
        obj = self.loader.loadModel(model_path)
        obj.reparentTo(self.render)
        obj.setPos(0, 0, 0)
        obj.setScale(1, 1, 1)
        logger.debug(f'Object model loaded from path: {model_path}')
        return obj

    def create_new_object(self):
        # Create a new cube object and add to the list
        new_obj = self.create_object_model("models/box")

        self.objects.append(new_obj)

        # Update the properties window to reflect the new object
        if hasattr(self, 'object_properties_window'):
            self.object_properties_window.update_properties()

    def move_camera_task(self, task):
        # Movement for the keys
        if self.keyMap["up"]:
            self.camera.setY(self.camera.getY() + self.movement_step)
            logger.debug(f'Camera moved up to position: {self.camera.getPos()}')
            self.keyMap["up"] = False  # Reset the key state

        if self.keyMap["down"]:
            self.camera.setY(self.camera.getY() - self.movement_step)
            logger.debug(f'Camera moved down to position: {self.camera.getPos()}')
            self.keyMap["down"] = False  # Reset the key state

        if self.keyMap["left"]:
            self.camera.setX(self.camera.getX() - self.movement_step)
            logger.debug(f'Camera moved left to position: {self.camera.getPos()}')
            self.keyMap["left"] = False  # Reset the key state

        if self.keyMap["right"]:
            self.camera.setX(self.camera.getX() + self.movement_step)
            logger.debug(f'Camera moved right to position: {self.camera.getPos()}')
            self.keyMap["right"] = False  # Reset the key state

        if self.keyMap["vup"]:
            self.camera.setZ(self.camera.getZ() + self.vertical_step)
            logger.debug(f'Camera moved up vertically to position: {self.camera.getPos()}')
            self.keyMap["vup"] = False  # Reset the key state

        if self.keyMap["vdown"]:
            self.camera.setZ(self.camera.getZ() - self.vertical_step)
            logger.debug(f'Camera moved down vertically to position: {self.camera.getPos()}')
            self.keyMap["vdown"] = False  # Reset the key state

        return Task.cont

    def set_key(self, key, value):
        self.keyMap[key] = value
        logger.debug(f'Set key {key} to {value}.')
        if value:  # Play sound only when key is pressed
            self.play_move_sound()

    def reset_camera_position(self):
        self.reset_camera()
        self.play_move_sound()  # Play sound when the camera is reset

    def play_move_sound(self):
        self.move_sound.play()
        logger.info('Move sound played.')

    def update_object(self, obj_index, pos, scale):
        # Update the specified object
        if 0 <= obj_index < len(self.objects):
            obj = self.objects[obj_index]
            obj.setPos(*pos)
            obj.setScale(*scale)
            logger.info(f'Updated object {obj_index} to position {pos} and scale {scale}.')
        
        # Update the Tkinter object properties window
        if hasattr(self, 'object_properties_window'):
            self.object_properties_window.update_properties()

class ObjectPropertiesWindow(tk.Toplevel):
    def __init__(self, parent, panda_app):
        super().__init__(parent)
        self.panda_app = panda_app
        self.title("Properties")

        self.current_index = 0  # Initialize current_index
        self.create_widgets()

    def create_widgets(self):
        self.object_var = tk.StringVar()
        self.object_var.set("Select Object")

        tk.Label(self, text="Select Object").pack()
        self.object_menu = ttk.Combobox(self, textvariable=self.object_var)
        self.object_menu.pack()
        self.object_menu.bind("<<ComboboxSelected>>", self.on_object_selection)

        tk.Label(self, text="Position (x, y, z):").pack()
        self.pos_entry = tk.Entry(self)
        self.pos_entry.pack()

        tk.Label(self, text="Scale (x, y, z):").pack()
        self.scale_entry = tk.Entry(self)
        self.scale_entry.pack()

        self.update_button = tk.Button(self, text="Update Object", command=self.update_object)
        self.update_button.pack()

        self.create_button = tk.Button(self, text="Create New Object", command=self.create_new_object)
        self.create_button.pack()

        # Update the dropdown menu to include existing objects
        self.update_object_menu()

    def update_properties(self):
        if not self.panda_app.objects:
            return  # Exit if there are no objects

        # Update only if current_index is within bounds
        if 0 <= self.current_index < len(self.panda_app.objects):
            obj = self.panda_app.objects[self.current_index]
            pos = obj.getPos()
            scale = obj.getScale()

            self.pos_entry.delete(0, tk.END)
            self.pos_entry.insert(0, f"{pos.getX():.2f}, {pos.getY():.2f}, {pos.getZ():.2f}")

            self.scale_entry.delete(0, tk.END)
            self.scale_entry.insert(0, f"{scale.getX():.2f}, {scale.getY():.2f}, {scale.getZ():.2f}")

    def update_object(self):
        try:
            pos = tuple(map(float, self.pos_entry.get().split(',')))
            scale = tuple(map(float, self.scale_entry.get().split(',')))
            if len(pos) == 3 and len(scale) == 3:
                self.panda_app.update_object(self.current_index, pos, scale)
            else:
                raise ValueError
        except ValueError:
            # Show an error message if there's a problem with the input values
            messagebox.showerror("Invalid Input", "Please enter valid numbers in the format 'x, y, z' for position and scale.")
            logger.error('Invalid input for position or scale.')

    def on_object_selection(self, event):
        selected = self.object_var.get()
        if selected.startswith("Object"):
            try:
                self.current_index = int(selected.split(" ")[1])  # Extract the index from the "Object X" string
                self.update_properties()
            except (IndexError, ValueError):
                self.current_index = 0
                self.update_properties()
                logger.error(f'Error selecting object: {selected}')

    def create_new_object(self):
        self.panda_app.create_new_object()
        self.update_object_menu()
        self.current_index = len(self.panda_app.objects) - 1  # Select the new object
        self.object_var.set(f"Object {self.current_index}")
        self.update_properties()

    def update_object_menu(self):
        self.object_menu['values'] = [f"Object {i}" for i in range(len(self.panda_app.objects))] + ["Create New Object"]

class TkinterApp(tk.Tk):
    def __init__(self, panda_app):
        super().__init__()
        self.panda_app = panda_app
        self.title("Movement")

        self.load_buttons()

        # Create the object properties window
        self.object_properties_window = ObjectPropertiesWindow(self, panda_app)

    def load_buttons(self):
        btn_up = self.create_button("up.png", lambda: self.panda_app.set_key("up", True), lambda: self.panda_app.set_key("up", False))
        btn_down = self.create_button("down.png", lambda: self.panda_app.set_key("down", True), lambda: self.panda_app.set_key("down", False))
        btn_left = self.create_button("left.png", lambda: self.panda_app.set_key("left", True), lambda: self.panda_app.set_key("left", False))
        btn_right = self.create_button("right.png", lambda: self.panda_app.set_key("right", True), lambda: self.panda_app.set_key("right", False))
        btn_center = self.create_button("center.png", self.panda_app.reset_camera_position, None)
        btn_vup = self.create_button("vup.png", lambda: self.panda_app.set_key("vup", True), lambda: self.panda_app.set_key("vup", False))
        btn_vdown = self.create_button("vdown.png", lambda: self.panda_app.set_key("vdown", True), lambda: self.panda_app.set_key("vdown", False))

        btn_up.grid(row=0, column=1)
        btn_vup.grid(row=0, column=0)  # Place the vup button next to the up button
        btn_vdown.grid(row=0, column=2)  # Place the vdown button next to the up button
        btn_left.grid(row=1, column=0)
        btn_center.grid(row=1, column=1)  # Place the center button in the middle of the dpad
        btn_right.grid(row=1, column=2)
        btn_down.grid(row=2, column=1)

    def create_button(self, image_path, command_on_press, command_on_release):
        image = Image.open(image_path)
        image = image.resize((50, 50), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        button = tk.Button(self, image=photo)
        button.image = photo  # Keep a reference to avoid garbage collection
        
        # Bind the button press event
        button.bind("<ButtonPress-1>", lambda event: command_on_press())
        
        # Bind the button release event only if command_on_release is not None
        if command_on_release:
            button.bind("<ButtonRelease-1>", lambda event: command_on_release())
        
        return button

def run_apps():
    panda_app = _3DStage()
    tk_app = TkinterApp(panda_app)
    tk_app.update_idletasks()
    tk_app.update()

    def update_tk_app(task):
        tk_app.update_idletasks()
        tk_app.update()
        return Task.cont

    panda_app.taskMgr.add(update_tk_app, "update_tk_app")
    panda_app.run()

if __name__ == "__main__":
    run_apps()
