class Menu:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.children = []
    
    def appendChild(child):
        child.parent = self
        self.children.append(child)