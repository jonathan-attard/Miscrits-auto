import pyautogui
import pygetwindow as gw
from PIL import Image


class Window:
    def __init__(self):
        self.title = "Miscrits"
        
        # Get the window by title using pygetwindow
        self.active_window = None
        for window in gw.getWindowsWithTitle(self.title):
            if window.title == self.title:
                self.active_window = window
                break

        if not self.active_window:
            raise Exception(f"No window found with title '{self.title}'")

        # Get the window's region for the screenshot
        self.window_rect = (
            self.active_window.left,
            self.active_window.top,
            self.active_window.width,
            self.active_window.height
        )

        # Optional: print window position for debugging
        print(f"Window position: {self.window_rect}")

    def get_image(self) -> Image.Image:
        # Ensure the coordinates are valid and within screen bounds
        screen_width, screen_height = pyautogui.size()

        x, y, w, h = self.window_rect
        if w <= 0 or h <= 0:
            raise Exception("Invalid window size.")

        # NOTE: pyautogui handles multi-monitor coordinates (negative x/y)
        frame = pyautogui.screenshot(region=(x, y, w, h))
        return frame


def main():
    w = Window()
    image = w.get_image()
    image.show()  # Opens the screenshot
    # image.save("screenshot.png")  # Uncomment to save


if __name__ == "__main__":
    main()
