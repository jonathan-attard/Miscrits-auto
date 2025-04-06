import numpy as np
import pyautogui
import pygetwindow as gw
from win32gui import (
    FindWindow,
    GetWindowRect,
    SetForegroundWindow,
    GetClientRect,
    ClientToScreen,
)
from mss import mss
import cv2
import time
from common import *

"""
https://stackoverflow.com/questions/35097837/capture-video-data-from-screen-in-python
"""


class Window:
    def __init__(self, resize_window=True):
        self.window_handle = FindWindow(None, WINDOW_TITLE)
        self.sct = mss()  # Create mss object only once

        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None

        self.resize_window = resize_window
        self.frame = None

    def show(self):
        SetForegroundWindow(self.window_handle)
        time.sleep(0.01)

    def point_to_winodw(self, x, y):
        x += self.x1
        y += self.y1
        return x, y

    def bbox_to_window(self, x1, y1, x2, y2):
        x1 += self.x1
        y1 += self.y1
        x2 += self.x1
        y2 += self.y1

        return x1, y1, x2, y2

    def get_frame(self):
        client_rect = GetClientRect(self.window_handle)
        client_to_screen = ClientToScreen(
            self.window_handle, (client_rect[0], client_rect[1])
        )

        self.x1 = client_to_screen[0]
        self.y1 = client_to_screen[1]
        self.width = client_rect[2] - client_rect[0]
        self.height = client_rect[3] - client_rect[1]
        self.x2 = self.x1 + self.width
        self.y2 = self.y1 + self.height


        bounding_box = {
            "top": self.y1,  # Y-coordinate of the client area
            "left":self.x1,  # X-coordinate of the client area
            "width": self.width,  # Width of the client area
            "height": self.height,  # Height of the client area
        }

        # Grab the screenshot of the window
        sct_img = self.sct.grab(bounding_box)
        frame = np.array(sct_img)[:, :, :3]

        if self.resize_window:
            frame = cv2.resize(frame, WINDOW_RESIZE)
        self.frame = frame

        return frame


    def stream(self):
        while True:
            frame = self.get_frame()  # Get the frame (assuming this method exists)
            if frame is None:
                break
            
            cv2.imshow("Window Capture", frame)
            key = (cv2.waitKey(1) & 0xFF)
            if key == ord('a'):
                self.save_image(frame)
            elif key == ord('q'):
                break
        cv2.destroyAllWindows()

    def save_image(frame):
        pass

def main():
    w = Window()
    w.show()
    w.stream()


if __name__ == "__main__":
    main()
