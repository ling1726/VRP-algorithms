class Step():

    def __init__(self):
        self.capacity = 0.
        self.battery = 0.
        self.arrivalTime = 0.
        self.departTime = 0.
        self.windowStart = 0.
        self.windowEnd = 0.
        self.id = ''

    def __str__(self):
        string = "id: "+self.id+"\n"
        string += "capacity: "+str(self.capacity)+"\n"
        string += "battery: "+str(self.battery)+"\n"
        string += "arrivalTrine: "+str(self.arrivalTime)+"\n"
        string += "departTime: "+str(self.departTime)+"\n"
        string += "windowStart: "+str(self.windowStart)+"\n"
        string += "windowEnd: "+str(self.windowEnd)+"\n"
        return string
