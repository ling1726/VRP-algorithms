from NB.instance.node import Node
#from node import Node #UNCOMMENT THIS & COMMENT ABOVE FOR SEQINS TO WORK

# Customer class with customer specific logic
class Customer(Node):

    __metaclass__ = Node

    def __init__(self):
        Node.__init__(self)