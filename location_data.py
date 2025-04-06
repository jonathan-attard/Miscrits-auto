import yaml
from enum import Enum
from common import *

class LocationType(Enum):
    POINT = 0
    BOUNDINGBOX = 1

class Location(Enum):
    CENTER = 0
    TOP = 1
    BOTTOM = 2
    RIGHT = 3
    LEFT = 4

class Point:
    name: str = None
    location: Location = Location.CENTER
    x = None
    y = None
    location_type = LocationType.POINT

    def __repr__(self):
        return str(self.__dict__)

class BoundingBox:
    name: str = None
    location: Location = Location.CENTER
    x1 = None
    y1 = None
    x2 = None
    y2 = None
    location_type = LocationType.BOUNDINGBOX

    def __repr__(self):
        return str(self.__dict__)

class ViewType(Enum):
    TEST = -1
    DEFAULT = 0
    BATTLE = 1
    BATTLECAPTURED = 2
    SUMMARY = 3
    SUMMARYCAPTURE = 4

class View:
    def __init__(self, view_type):
        self.view_type: ViewType = view_type
        self.positions: dict = {}

    def items(self):
        return self.positions.items()

    def __getattr__(self, name):
        # Allows l.default.encounter
        try:
            return self.positions[name.lower()]
        except KeyError:
            raise AttributeError(f"No position named '{name}' in view '{self.view_type.name}'")
        
    def __getitem__(self, name):
        # Allows l.default.encounter
        try:
            return self.positions[name.lower()]
        except KeyError:
            raise AttributeError(f"No position named '{name}' in view '{self.view_type.name}'")

    def __repr__(self):
        return str(self.positions)

class LocationData:
    def __init__(self, location_data_path = LOCATION_DATA_PATH):
        self._views = {}

        with open(location_data_path, 'r') as f:
            data = yaml.safe_load(f)
            positions = data["positions"]

            for view_name, view_positions in positions.items():
                view_type = self.match_view(view_name)
                view = View(view_type)

                for _, entry in view_positions.items():
                    name = entry["name"].lower()
                    location = self.match_location(entry["location"])
                    location_type = self.match_location_type(entry["location_type"])

                    if location_type == LocationType.POINT:
                        point = Point()
                        point.x = round(entry["x"] * WindowSize.width)
                        point.y = round(entry["y"] * WindowSize.height)
                        point.name = name
                        point.location = location
                        point.location_type = location_type
                        view.positions[name] = point

                    elif location_type == LocationType.BOUNDINGBOX:
                        bbox = BoundingBox()
                        bbox.x1 = round(entry["x1"] * WindowSize.width)
                        bbox.y1 = round(entry["y1"] * WindowSize.height)
                        bbox.x2 = round(entry["x2"] * WindowSize.width)
                        bbox.y2 = round(entry["y2"] * WindowSize.height)
                        bbox.name = name
                        bbox.location = location
                        bbox.location_type = location_type
                        view.positions[name] = bbox

                self._views[view_type.name.lower()] = view

    def __getattr__(self, name):
        # Allows l.default or l.battle
        try:
            return self._views[name.lower()]
        except KeyError:
            raise AttributeError(f"No view named '{name}'")
        
    def __getitem__(self, name):
        # Allows l.default or l.battle
        try:
            return self._views[name.lower()]
        except KeyError:
            raise AttributeError(f"No view named '{name}'")

    @staticmethod
    def match_location(location_str):
        try:
            return Location[location_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid location: {location_str}")

    @staticmethod
    def match_view(view_str):
        try:
            return ViewType[view_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid view type: {view_str}")

    @staticmethod
    def match_location_type(location_type_str):
        try:
            return LocationType[location_type_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid location type: {location_type_str}")

    def __repr__(self):
        return str(self._views)


if __name__ == "__main__":
    l = LocationData()
    print(l.battle.difficulty.x1)
    print(l.default.encounter.y)
    print(l.default["encounter"].y)
    print(l["default"]["encounter"].y)
    print(l.default.items())

