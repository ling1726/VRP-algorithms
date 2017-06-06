from NB.instance.node import Node
#from node import Node #UNCOMMENT THIS & COMMENT OUT ABOVE IMPORT FOR SEQINS TO WORK
import copy

# Charger class with charger specific logic
class Charger(Node):

    __metaclass__ = Node

    def __init__(self):
        Node.__init__(self)
        self.load_time = 0
        self.id_counter = 0

    def generate_clone(self):
        self.id_counter+=1
        tmp = copy.deepcopy(self)
        tmp.id = self.id + "_"+str(self.id_counter)
        return tmp

    def equal_to(self, other_charger):
        short_id_1 = self.id
        short_id_2 = other_charger.id

        if self.id.find("_") != -1:
            short_id_1,tmp,tmp = other_charger.id.partition("_")
        if self.id.find("_") != -1:
            short_id_2,tmp,tmp = other_charger.id.partition("_")
        return short_id_1 == short_id_2
