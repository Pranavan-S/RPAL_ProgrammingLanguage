class TreeNode:
    def __init__(self, value):
        self.parent = None
        self.children = []
        self.value = value

    def add_child(self, child):
        child.parent = self
        self.children.append(child)
