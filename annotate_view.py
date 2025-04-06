import copy
import time
import cv2
import numpy as np
from location_data import LocationData, ViewType, LocationType
from ocr import OCR


class AnnotateTest:
    def __init__(self, show_roi=False, gpu=True):
        self.ocr = OCR(gpu=gpu)

        self.show_roi = show_roi
        self.ocr_names = []
        self.color_names = []

        self.location_data = None
        self.view = None
        self.image = None
        self.image_draw = None

        pass

    def start(self, view: ViewType, image, ocr_names=None, color_names=None, location_data_path=None):
        if ocr_names is None:
            ocr_names = []
        if color_names is None:
            color_names = []
        self.ocr_names = ocr_names
        self.color_names = color_names
        self.view = view
        self.image = image
        self.image_draw = copy.deepcopy(image)

        while True:
            self.location_data = LocationData(location_data_path=location_data_path)
            self.read_annotation()

            cv2.imshow("Annotation Viewer", self.image_draw)
            key = (cv2.waitKey(1) & 0xFF)
            if key == ord('q'):
                break

            time.sleep(1)
        cv2.destroyAllWindows()

    def get_frame_roi(self, position):
        if  position.location_type == LocationType.BOUNDINGBOX:
            x1, y1, x2, y2 = position.x1, position.y1, position.x2, position.y2
            frame = self.image            
            frame_roi = frame[y1:y2, x1:x2]
            return frame_roi

        return None
    
    def get_pixel(self, position):
        if  position.location_type == LocationType.POINT:
            x, y = position.x, position.y
            frame = self.image            
            pixel = frame[y][x]
            return pixel

        return None


    def read_annotation(self):
        data = self.location_data[self.view.name]
        for position_name, position in data.items():

            name = position.name
            location_type = position.location_type

            if location_type == LocationType.POINT:
                x, y = position.x, position.y

                if name in self.color_names:
                    pixel = self.get_pixel(position)
                    print(name, pixel)
                    pixel_image = np.full((300, 300, 3), pixel, dtype=np.uint8)
                    cv2.imshow(name, pixel_image)

                # Draw the point (circle)
                cv2.circle(self.image_draw, (x, y), radius=5, color=(0, 255, 0), thickness=-1)
                # Put name near the point
                cv2.putText(
                    self.image_draw,
                    name,
                    (x + 5, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA,
                )
                

            elif location_type == LocationType.BOUNDINGBOX:
                x1, y1 = position.x1, position.y1
                x2, y2 = position.x2, position.y2

                # print(f"'{name}', {self.ocr_names}", name in self.ocr_names)
                frame_roi = self.get_frame_roi(position)
                if name in self.ocr_names:
                    ocr_text = self.ocr.read_text(frame_roi)
                    text = f"{name}: {ocr_text}"
                    print(text)
                else:
                    text = name

                cv2.rectangle(self.image_draw, (x1, y1), (x2, y2), color=(255, 0, 0), thickness=2)
                cv2.putText(
                    self.image_draw,
                    text,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 0),
                    1,
                    cv2.LINE_AA,
                )

                if self.show_roi and name in self.ocr_names:
                    cv2.imshow(name, cv2.resize(frame_roi, (300, 300)))
    


def main():
    view = ViewType.TEST
    num = 5 # 10
    image_path = f"temp/annotations/{num}/input.png"
    # location_data_path = f"temp/annotations/{num}/annotations.yaml"
    location_data_path = "data/locations.yaml"
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)  # Read image in color mode

    ocr_names = [
        # "continue text",
        # "Gold",
        # "keep text",
        # "Capture Rate"
    ]
    color_names = [
        "Level 1",
        "Level 2",
        "Level 3",
        "Level 4",
    ]
    ocr_names = [x.lower() for x in ocr_names]
    color_names = [x.lower() for x in color_names]
    print(ocr_names, color_names)


    a = AnnotateTest(show_roi=True)
    a.start(view, image, ocr_names=ocr_names, color_names=color_names, location_data_path=location_data_path)


if __name__ == "__main__":
    main()
