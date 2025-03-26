import json

class Device:
    def __init__(self, device_id, name, type, status, settings):
        self.id = device_id
        self.name = name
        self.type = type
        self.status = bool(status)
        self.settings = json.loads(settings) if settings else {}

    def __repr__(self):
        return f"<Device {self.name} (Type: {self.type}) Status: {'ON' if self.status else 'OFF'} Settings: {self.settings}>"

class DeviceManager:
    def __init__(self, db):
        self.db = db

    def get_device(self, name):
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT id, name, type, status, setting FROM devices WHERE name = %s", (name,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return Device(*row)
        return None

    def turn_on(self, name):
        cursor = self.db.connection.cursor()
        cursor.execute("UPDATE devices SET status = 1 WHERE name = %s", (name,))
        self.db.connection.commit()
        cursor.close()

    def turn_off(self, name):
        cursor = self.db.connection.cursor()
        cursor.execute("UPDATE devices SET status = 0 WHERE name = %s", (name,))
        self.db.connection.commit()
        cursor.close()

    def toggle(self, name):
        device = self.get_device(name)
        if device:
            new_status = 0 if device.status else 1
            cursor = self.db.connection.cursor()
            cursor.execute("UPDATE devices SET status = %s WHERE name = %s", (new_status, name))
            self.db.connection.commit()
            cursor.close()

    def change_setting(self, name, key, value):
        device = self.get_device(name)
        if device:
            device.settings[key] = value  # update setting dict
            new_settings = json.dumps(device.settings)

            cursor = self.db.connection.cursor()
            cursor.execute("UPDATE devices SET setting = %s WHERE name = %s", (new_settings, name))
            self.db.connection.commit()
            cursor.close()

    def get_all_devices(self):
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT id, name, type, status, setting FROM devices")
        rows = cursor.fetchall()
        cursor.close()
        return [Device(*row) for row in rows]
