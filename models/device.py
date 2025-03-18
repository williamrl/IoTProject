# Base class for a generic IoT device
class Device:
    def __init__(self, device_id: str, name: str, status: bool = False):
        # Initialize the device with an ID, name, and status (default is OFF)
        self.device_id = device_id
        self.name = name
        self.status = status

    def turn_on(self) -> None:
        # Turn the device ON
        self.status = True
        print(f"{self.name} is now ON")

    def turn_off(self) -> None:
        # Turn the device OFF
        self.status = False
        print(f"{self.name} is now OFF")

    def get_status(self) -> bool:
        # Return the current status of the device (ON or OFF)
        return self.status

    def __repr__(self) -> str:
        # String representation of the device for debugging purposes
        return f"Device(device_id={self.device_id}, name={self.name}, status={self.status})"


# Subclass for a lighting-specific IoT device
class LightingDevice(Device):
    # Default values for brightness and color
    DEFAULT_BRIGHTNESS = 100
    DEFAULT_COLOR = "white"

    def __init__(self, device_id: str, name: str, brightness: int = DEFAULT_BRIGHTNESS, color: str = DEFAULT_COLOR):
        # Initialize the lighting device with additional attributes: brightness and color
        super().__init__(device_id, name)
        self.brightness = brightness
        self.color = color

    def set_brightness(self, level: int) -> None:
        # Set the brightness level (must be between 0 and 100)
        if 0 <= level <= 100:
            self.brightness = level
        else:
            raise ValueError("Brightness level must be between 0 and 100")

    def set_color(self, color: str) -> None:
        # Set the color of the lighting device
        self.color = color

    def __repr__(self) -> str:
        # String representation of the lighting device for debugging purposes
        return f"LightingDevice(device_id={self.device_id}, name={self.name}, status={self.status}, brightness={self.brightness}, color={self.color})"
