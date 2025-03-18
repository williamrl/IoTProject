class Device:
    def __init__(self, device_id: str, name: str, status: bool = False):
        self.device_id = device_id
        self.name = name
        self.status = status

    def turn_on(self) -> None:
        self.status = True
        print(f"{self.name} is now ON")

    def turn_off(self) -> None:
        self.status = False
        print(f"{self.name} is now OFF")

    def get_status(self) -> bool:
        return self.status

    def __repr__(self) -> str:
        return f"Device(device_id={self.device_id}, name={self.name}, status={self.status})"


# Subclasses
class LightingDevice(Device):
    DEFAULT_BRIGHTNESS = 100
    DEFAULT_COLOR = "white"

    def __init__(self, device_id: str, name: str, brightness: int = DEFAULT_BRIGHTNESS, color: str = DEFAULT_COLOR):
        super().__init__(device_id, name)
        self.brightness = brightness
        self.color = color

    def set_brightness(self, level: int) -> None:
        if 0 <= level <= 100:
            self.brightness = level
        else:
            raise ValueError("Brightness level must be between 0 and 100")

    def set_color(self, color: str) -> None:
        self.color = color

    def __repr__(self) -> str:
        return f"LightingDevice(device_id={self.device_id}, name={self.name}, status={self.status}, brightness={self.brightness}, color={self.color})"
