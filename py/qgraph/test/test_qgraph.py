import pytest

from qgraph.qgraph import QueryKey, str_to_binary, Metadata, Node, Graph


class TestUtils:
    def test_str_to_binary_returns_binary_str_of_input_str(self):
        assert str_to_binary("abc") == "110000111000101100011"

class TestKey:
    def test_query_key_bin_is_binary_of_query(self):
        query = "iphone 2017"
        key = QueryKey(query)

        assert key.bin == str_to_binary(query)

    def test_query_key__iter__(self):
        iters = 0
        query = "abc"
        key = QueryKey(query)
        for _ in key:
            iters += 1

        assert iters == len(key)


class TestMetadata:
    def test_can_create_metadata(self):
        meta = Metadata(0, 0, 0)
        assert isinstance(meta.bottiness, int)



class TestNode:
    def test_can_create_root_node(self):
        node = Node("bloomberg")
        assert node.left is None
        assert node.right is None

    def test_add_child_inserts_0_at_left_child(self):
        node = Node("foo")
        child = Node("bar")

        node.add_child(child)

        assert isinstance(node.left, Node)
        assert node.right is None

    def test_add_child_inserts_1_at_right_child(self):
        node = Node("foo")
        child = Node("zoo")

        node.add_child(child)

        assert isinstance(node.right, Node)
        assert node.left is None


class TestGraph:
    def test_can_create_graph_using_root_node(self):
        g = Graph()
        assert isinstance(g.root, Node)
        assert g.query_count == 0
        assert g.node_count == 1
        assert g.root.query == QueryKey("")

    def test_can_add_node_to_graph_when_node_is_not_in_graph(self):
        g = Graph()
        g.add("foo")
        assert g.node_count == len(QueryKey("foo")) + 1

        assert g.root.query == ""

    def test_can_find_query_in_graph_when_query_is_present(self):
        g = Graph()
        g.add("bar")
        assert "bar" in g

    def test_can_not_find_query_in_graph_when_query_is_not_present(self):
        g = Graph()
        g.add("foo")
        assert "bar" not in g

    def test_get_returns_node_when_query_exists_in_graph(self):
        g = Graph()
        g.add("zoo")
        g.add("blues")
        node = g.get("zoo")

        assert isinstance(node, Node)
        assert node.query == QueryKey("zoo")

    def test_get_returns_none_when_query_does_not_exist_in_graph(self):
        g = Graph()
        g.add("bar")
        node = g.get("nothing")

        assert node is None

    def test_node_count_property_increments_for_every_added_node(self):
        g = Graph()
        g.add("foo")
        g.add("bar")
        g.add("baz")
        g.add("zoo")

        assert g.query_count == 4
        assert g.node_count == 62

    @pytest.mark.skip(reason="Deprecated")
    def test_update_node_metadata_updates_metdata_for_node_when_node_in_graph(self):
        g = Graph()
        g.add("foo")
        g.add("bar")
        assert "foo" in g
        g.update_node_metadata("foo", first_name="Ava", last_name="Noel")

        node = g.get("foo")
        node.query.value["first_name"] == "Ava"
        node.query.value["last_name"] == "Noel"

    @pytest.mark.skip(reason="Not implemented")
    def test_can_print_graph(self):
        g = Graph()
        g.add("nike")
        g.add("foo")

        g.print()

    def test_stats_increments_seeks_for_every_seek_operation_in_graph(self):
        g = Graph()
        g.add("foo")
        g.add("bar")

        assert g.seeks == 0

        _ = "foo" in g

        assert g.seeks == 1

    def test_stats_increments_hits_for_every_successful_find_operation_in_graph(self):
        g = Graph()
        g.add("foo")
        g.add("bar")

        assert g.hits == 0

        _ = "foo" in g

        assert g.hits == 1

    def test_stats_increments_misses_for_every_unsucessful_find_operation_in_graph(self):
        g = Graph()
        g.add("foo")
        g.add("bar")

        assert g.misses == 0

        _ = "zoo" in g

        assert g.misses == 1

    def test_adding_query_to_graph_increments_graph_stats_queries_size_raw_bytes(self):
        g = Graph()

        assert g.queries_size_raw_bytes == 0

        g.add("foo")
        g.add("bar")

        assert g.queries_size_raw_bytes ==6

    def test_adding_query_to_graph_increments_graph_stats_queries_size_actual_bits(self):
        g = Graph()

        assert g.queries_size_raw_bytes == 0

        g.add("foo")
        g.add("bar")

        assert g.queries_size_actual_bits == 38.0
 