

class Scan:

    def __init__(self, time, location, power):
        self.location = location
        self.time = time
        self.power = power

    def __str__(self):
        output = 'Location: '+ str(self.location)
        output += ' Time: '+ str(self.time)
        output += ' Power: '+ str(self.power)
        return output