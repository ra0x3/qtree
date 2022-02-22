import pytest

from qgraph.qgraph import QueryKey, str_to_binary, Metadata, Node, LightKey, LightNode, HistoryNode, Graph, is_exclusively_01


class TestUtils:
    def test_str_to_binary_returns_binary_str_of_input_str(self):
        assert str_to_binary(b"abc") == b"110000111000101100011"

    def test_is_exclusively_01_returns_true_for_binary_str_of_0s_and_1s(self):
        assert is_exclusively_01(b"110000111000101100011")

    def test_is_exclusively_01_01_returns_false_for_non_binary_str(self):
        assert not is_exclusively_01("abc")

class TestKey:
    def test_query_key_bin_is_binary_of_query(self):
        query = b"iphone 2017"
        key = QueryKey(query)

        assert key.bin == str_to_binary(query)

    def test_query_key__iter__(self):
        iters = 0
        query = b"abc"
        key = QueryKey(query)
        for _ in key:
            iters += 1

        assert iters == len(key)


class TestMetadata:
    def test_can_create_metadata(self):
        meta = Metadata(0, 0, 0)
        assert isinstance(meta.bottiness, int)



class TestHistoryNode:
    def test_can_create_root_node(self):
        node = HistoryNode(b"bloomberg")
        assert node.left is None
        assert node.right is None

    def test_add_child_inserts_0_at_left_child(self):
        node = HistoryNode(b"foo")
        child = HistoryNode(b"bar")

        node.add_child(child)

        assert isinstance(node.left, HistoryNode)
        assert node.right is None

    def test_add_child_inserts_1_at_right_child(self):
        node = HistoryNode(b"foo")
        child = HistoryNode(b"4400")

        node.add_child(child)

        assert isinstance(node.left, HistoryNode)
        assert node.right is None


class TestGraph:
    def test_can_create_graph_using_root_node(self):
        g = Graph()
        assert isinstance(g.root, Node)
        assert g.query_count == 0
        assert g.node_count == 1

        assert g.root.query == 50

    def test_can_add_node_to_graph_when_node_is_not_in_graph(self):
        g = Graph()
        g.add(b"foo")
        assert g.node_count == 4

    def test_can_find_query_in_graph_when_query_is_present(self):
        g = Graph()
        g.add(b"bar")
        assert b"bar" in g

    def test_can_not_find_query_in_graph_when_query_is_not_present(self):
        g = Graph()
        g.add(b"foo")
        assert b"bar" not in g

    def test_get_returns_node_when_query_exists_in_graph(self):
        g = Graph()
        g.add(b"zoo")
        g.add(b"blues")
        node = g.get(b"zoo")

        assert isinstance(node, LightNode)

    def test_get_returns_none_when_query_does_not_exist_in_graph(self):
        g = Graph()
        g.add(b"bar")
        node = g.get(b"nothing")

        assert node is None

    def test_node_count_property_increments_for_every_added_node(self):
        g = Graph()
        g.add(b"foo")
        g.add(b"bar")
        g.add(b"baz")
        g.add(b"zoo")

        assert g.query_count == 4
        assert g.node_count == 6

    @pytest.mark.skip(reason="Deprecated")
    def test_update_node_metadata_updates_metdata_for_node_when_node_in_graph(self):
        pass

    @pytest.mark.skip(reason="Not implemented")
    def test_can_print_graph(self):
        g = Graph()
        g.add(b"nike")
        g.add(b"foo")

        g.print()

    def test_stats_increments_seeks_for_every_seek_operation_in_graph(self):
        g = Graph()
        g.add(b"foo")
        g.add(b"bar")

        assert g.seeks == 0

        _ = b"foo" in g

        assert g.seeks == 1

    def test_stats_increments_hits_for_every_successful_find_operation_in_graph(self):
        g = Graph()
        g.add(b"foo")
        g.add(b"bar")

        assert g.hits == 0

        _ = b"foo" in g

        assert g.hits == 1

    @pytest.mark.skip(reason="Incorrect implementation")
    def test_stats_increments_misses_for_every_unsucessful_find_operation_in_graph(self):
        g = Graph()
        g.add(b"foo")
        g.add(b"bar")

        assert g.misses == 0

        _ = b"zoo" in g

        assert g.misses == 1


    def test_adding_query_to_graph_increments_graph_stats_queries_size_raw_bytes(self):
        g = Graph()

        assert g.queries_size_raw_bytes == 0

        g.add(b"foo")
        g.add(b"bar")

        assert g.queries_size_raw_bytes ==72

    def test_adding_query_to_graph_increments_graph_stats_queries_size_actual_bytes(self):
        g = Graph()

        assert g.queries_size_raw_bytes == 0

        g.add(b"foo")
        g.add(b"bar")

        assert g.queries_size_actual_bytes == 168

 