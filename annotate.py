import os
import cv2
from window import Window
from draw import annotate



class Annotate(Window):
    def __init__(self, directory='temp/annotations'):
        super().__init__()

        self.directory = directory

    def new_folder(self):
        if os.path.exists(self.directory):
            folders = [int(f) for f in os.listdir(self.directory) if os.path.isdir(os.path.join(self.directory, f)) and f.isnumeric()]
        else:
            folders = []

        if len(folders) == 0:
            new_folder = "1"
        else:
            folders.sort()
            new_folder = str(folders[-1] + 1)

        return new_folder

    def save_image(self, frame):
        folder_path = os.path.join(self.directory, self.new_folder())
        image_path = os.path.join(folder_path, 'input.png')
        yaml_path = os.path.join(folder_path, 'annotations.yaml')
        image_output_path = os.path.join(folder_path, 'output.png')
        os.makedirs(folder_path, exist_ok=False)
        cv2.imwrite(image_path, frame)

        annotate(image_path=image_path, yaml_path=yaml_path, image_output_path=image_output_path)



if __name__ == "__main__":
    a = Annotate()
    a.show()
    a.stream()