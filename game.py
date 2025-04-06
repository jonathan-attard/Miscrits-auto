import csv
from datetime import datetime
import os
import random
import time

import numpy as np
from location_data import LocationData, LocationType
from window import Window
from pyautogui import mouseDown, mouseUp
from ocr import OCR
import cv2

"""
Github issues :)
"""

class BattleInfo:
    capture_rate: int = None
    name: str = None

    def __repr__(self):
        return str(self.__dict__)
    
class BattleSummary:
    capture_rate: int = None
    name: str = None
    gold: int = None
    captued: bool = None
    levelups: list[bool] = []

    def __repr__(self):
        return str(self.__dict__)

class Game(Window):
    def __init__(self, gpu: bool=True, summary_path='data/summary.csv'):
        super().__init__()

        self.location_data = LocationData()

        self.ocr = OCR(gpu=gpu)

        self.battle_summary = BattleSummary()
        self.summary_path = summary_path


    def click(self, position):
        if position.location_type == LocationType.POINT:
            (x, y) = self.point_to_winodw(position.x, position.y)
            mouseDown(x=x, y=y)
            time.sleep(0.1)
            mouseUp()

        elif position.location_type == LocationType.BOUNDINGBOX:
            bbox = self.bbox_to_window(position.x1, position.y1, position.x2, position.y2)
            x1, y1, x2, y2 = bbox

            random_x = random.uniform(x1, x2)
            random_y = random.uniform(y1, y2)

            mouseDown(x=random_x, y=random_y)
            time.sleep(0.1)
            mouseUp()

    def show_frame(self, frame, name="frame display"):
        cv2.imshow(frame, name)

    def get_frame_roi(self, position):
        if  position.location_type == LocationType.BOUNDINGBOX:
            x1, y1, x2, y2 = position.x1, position.y1, position.x2, position.y2
            frame = self.frame            
            frame_roi = frame[y1:y2, x1:x2]
            return frame_roi

        return None

    def read_ocr(self, position):
        frame_roi = self.get_frame_roi(position)
        if frame_roi is not None:
            texts = self.ocr.read_text(frame_roi)
            if len(texts) == 1:
                return texts[0]

    def get_battle_info(self):
        battle_info = BattleInfo()

        # Capture Rate
        capture_rate = None
        position = self.location_data.battle["capture rate"]
        capture_rate_text = self.read_ocr(position)
        if capture_rate_text is not None and '%' == capture_rate_text[-1]:
            capture_rate = capture_rate_text[:-1]
            battle_info.capture_rate = int(capture_rate)

        # Name
        position = self.location_data.battle["name"]
        battle_info.name = self.read_ocr(position)

        print(battle_info)
        return battle_info
            
    def encounter(self):
        position = self.location_data.default.encounter
        self.click(position)

    def attack(self):
        position = self.location_data.battle.attack
        self.click(position)

    def capture(self):
        position = self.location_data.battle.capture
        self.click(position)

    def check_captured(self):
        position = self.location_data.BattleCaptured["Captured okay text"]
        text = self.read_ocr(position)
        if text is not None and text.lower() == 'okay':
            return True
        return False
    
    def captured_okay(self):
        position = self.location_data.BattleCaptured["Captured okay"]
        self.click(position)

    def check_summary(self):
        position = self.location_data.Summary["Rewards text"]
        text = self.read_ocr(position)
        if text is not None and 'reward' in text.lower():
            return True
        return False
    
    def summary_continue(self):
        position = self.location_data.Summary["continue"]
        self.click(position)
    
    def get_gold(self):
        position = self.location_data.Summary["Gold"]
        text = self.read_ocr(position)
        gold_num = int(text)
        return gold_num
    
    def check_summary_capture(self):
        position = self.location_data.SummaryCapture["Keep text"]
        text = self.read_ocr(position)
        if text is not None and 'keep' == text.lower():
            return True
        return False
    
    def summary_capture_keep(self):
        position = self.location_data.SummaryCapture["keep"]
        self.click(position)

    def get_pixel(self, position):
        if  position.location_type == LocationType.POINT:
            x, y = position.x, position.y
            frame = self.frame            
            pixel = frame[y][x]
            return pixel

        return None
    
    @staticmethod
    def color_similarity_lab(color1, color2):
        # Convert (R,G,B) to (1x1x3 BGR) for OpenCV
        color1_bgr = np.uint8([[color1[::-1]]])  # RGB to BGR
        color2_bgr = np.uint8([[color2[::-1]]])

        lab1 = cv2.cvtColor(color1_bgr, cv2.COLOR_BGR2LAB)[0][0].astype(np.float32)
        lab2 = cv2.cvtColor(color2_bgr, cv2.COLOR_BGR2LAB)[0][0].astype(np.float32)

        dist = np.linalg.norm(lab1 - lab2)
        similarity = 1 - (dist / 100)  # Normalize LAB distance
        return similarity

    def check_levelup(self):
        Levelup_color = [228, 229, 229]   # White
        Default_color = [69, 57, 46]      # Gray

        level_nums = ["Level 1", "Level 2", "Level 3", "Level 4"]

        levelups = []

        for i, level_num in enumerate(level_nums):
            position = self.location_data.Summary[level_num]
            pixel_color = self.get_pixel(position)

            levelup_similiarity = self.color_similarity_lab(pixel_color, Levelup_color)
            default_similiarity = self.color_similarity_lab(pixel_color, Default_color)
            
            if levelup_similiarity > 0.99:
                levelups.append(True)
            elif default_similiarity > 0.99:
                levelups.append(False)
            else:
                print('WARNING', level_num, levelup_similiarity, default_similiarity)
                levelups.append(None)
        self.battle_summary.levelups = levelups
        return levelups

    def levelup(self):
        # Enter function to level up
        pass

    def attack_kill(self):
        while True:
            self.attack()
            time.sleep(5)

            self.get_frame()
            battle_info = self.get_battle_info()

            # Is dead?
            if battle_info.capture_rate is None:
                break
    
    def start(self):
        while True:
            self.start_encounter()

            time.sleep(5)

    def start_encounter(self):
        self.show()
        time.sleep(1)

        # Start enoucnter
        self.get_frame()
        self.encounter()
        time.sleep(5)

        # start battle
        self.get_frame()
        battle_info = self.get_battle_info()

        # Saving stats
        self.battle_summary.capture_rate = battle_info.capture_rate
        self.battle_summary.name = battle_info.name

        if battle_info.capture_rate is None:
            return

        # Start catching condition
        capturing = False
        if battle_info.capture_rate < 30:
            capturing = True
            while True:
                self.attack()
                time.sleep(5)

                self.get_frame()
                battle_info = self.get_battle_info()

                # Probably dead
                if battle_info.capture_rate is None:
                    break

                # Catch condition
                if battle_info.capture_rate > 80:
                    self.capture()
                    time.sleep(5)
                    break
        else:
            self.attack_kill()

        # BattleCaptured
        if capturing:
            time.sleep(5)
            self.get_frame()

            if self.check_captured():
                # Log stats

                self.captured_okay()
            # If not captured, then failed, and kill.
            else:
                capturing = False
                self.attack_kill()
        
        # Summary
        time.sleep(5)
        self.get_frame()
        if self.check_summary():
            time.sleep(5)

            self.get_frame()
            self.battle_summary.gold = self.get_gold()

            self.check_levelup()

            self.summary_continue()

        # Summary Capture
        if capturing:
            time.sleep(5)
            self.get_frame()

            if self.check_summary_capture():
                self.summary_capture_keep()
        self.battle_summary.captued = capturing

        self.levelup()


        print(self.battle_summary)
        self.save_battle_summary(self.battle_summary.__dict__)

    def test(self):
        self.show()
        self.get_frame()

        self.check_levelup()

    def save_battle_summary(self, row):
        # Add timestamp to the row
        row['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        file_exists = os.path.isfile(self.summary_path)

        with open(self.summary_path, 'a', newline='') as csvfile:
            # Include 'timestamp' as part of the fieldnames
            fieldnames = list(row.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(row)



def main():
    g = Game()
    # g.start()
    g.test()

if __name__ == "__main__":
    main()