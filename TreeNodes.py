class TreeNode:
    """
    This class represents the AST Nodes. Each node has Parent, Children, and Value.
    """
    def __init__(self, value):
        self.parent = None
        self.children = []
        self.value = value

    def add_child(self, child):
        """
        This function is for adding children to an AST Node.
        :param child:
        :return:
        """
        child.parent = self
        self.children.append(child)

    @staticmethod
    def remove_child(child):
        child.parent.children.remove(child)
        child.parent = None
