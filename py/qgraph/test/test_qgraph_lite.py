import pytest

from qgraph.qgraph_lite import TreeNode, Tree, Children



class TestChildren:
    def test_can_add_child_nodes_to_children(self):
        c = Children()
        c.add(TreeNode(0x0))
        c.add(TreeNode(0x1))

        assert len(c) == 2
        assert TreeNode(0x0) in c

    def test_can_get_item_from_children(self):
        c = Children()
        c.add(TreeNode(0x0))
        c.add(TreeNode(0x1))

        child = c[TreeNode(0x0)]
        assert isinstance(child, TreeNode) and child.key == 0x0


class TestTreeNode:
    def test_can_add_children_to_tree_node(self):
        a = TreeNode(48)
        b = TreeNode(49)
        c = TreeNode(47)

        a.children.add(b)
        a.children.add(c)

        assert len(a.children) == 2


class Testtree:
    def test_can_instantiate_new_tree(self):
        t = Tree()
        assert isinstance(t.root, TreeNode)
        assert t.node_count == 1
        assert t.query_count == 0

    def test_can_add_a_new_node_to_tree(self):
        t = Tree()
        t.add(b"foo")

        assert t.query_count == 1
        assert b"foo"  in t

        # 3(foo) + 1(root)
        assert t.node_count == 4

    def test_can_add_multiple_new_nodes_to_tree(self):
        t = Tree()
        t.add(b"foo")
        t.add(b"bar")

        assert t.query_count == 2
        assert b"foo" in t
        assert b"bar" in t

        # 3(foo) + 3(bar) + 1(root)
        assert t.node_count == 7

    def test_can_add_multiple_nodes_with_same_starting_bytes(self):
        t = Tree()
        t.add(b"foo")
        t.add(b"for")
        t.add(b"froze")

        assert t.query_count == 3

        assert b"foo" in t
        assert b"for" in t
        assert b"froze" in t

        # 3(foo) + 1(for) + 4(froze) + 1(root)
        assert t.node_count == 9