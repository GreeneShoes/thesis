from time import strftime, localtime

class Alarm:
    def __init__(self, description, location ,time=''):
        if time == '':
            self.time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        else:
            self.time = time

        self.description = description
        self.location = location

    def __str__(self):
        return '[*]Alarm: '+str(self.time) + '. Location: ' + str(self.location) + '  '+ str(self.description)
