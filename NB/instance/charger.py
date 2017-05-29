from NB.instance.node import Node
#from node import Node #UNCOMMENT THIS & COMMENT OUT ABOVE IMPORT FOR SEQINS TO WORK

# Charger class with charger specific logic
class Charger(Node):
    def __init__(self):
        Node.__init__(self)
