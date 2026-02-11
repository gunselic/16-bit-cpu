class Memory:
    def __init__(self, size=256):
        self.data = [0] * size

    def load(self, address):
        return self.data[address]

    def store(self, address, value):
        if 0 <= address < len(self.data):
             self.data[address] = value & 0xFFFF

