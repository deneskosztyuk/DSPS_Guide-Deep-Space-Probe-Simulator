class DataModel:
    def __init__(self):
        self.data = {
            "temperature": [],
            "humidity": [],
            "pressure": [],
            "altitude": [],
        }
        self.is_connected = False

    def update_data(self, new_data):
        for key in self.data:
            if key in new_data:
                self.data[key].append(new_data[key])
    
    def get_data(self, key):
        return self.data.get(key, [])

    def get_latest(self, key):
        if self.data.get(key):
            return self.data[key][-1]
        return 0

    def toggle_connection(self):
        self.is_connected = not self.is_connected
