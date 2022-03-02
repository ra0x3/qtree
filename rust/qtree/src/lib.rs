
mod node {
    use std::cell::RefCell;
    use std::collections::HashMap;
    use std::hash::{Hash, Hasher};
    use std::rc::Rc;

    #[derive(Debug, Clone, PartialEq, Eq)]
    pub struct Node {
        pub key: u8,
        pub children: HashMap<u8, Rc<RefCell<Node>>>,
    }

    impl Hash for Node {
        fn hash<H: Hasher>(&self, state: &mut H) {
            self.key.hash(state);
        }
    }

    impl Node {
        pub fn new(key: u8) -> Self {
            Node {
                key,
                children: HashMap::new(),
            }
        }

        pub fn add_child(&mut self, other: Node) {
            let key = other.key.clone();
            self.children.insert(key, Rc::new(RefCell::new(other)));
        }

        pub fn get_child(&self, key: &u8) -> Option<&Rc<RefCell<Node>>> {
            self.children.get(key)
        }

        pub fn contains_child(&self, key: &u8) -> bool {
            self.children.contains_key(key)
        }
    }

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        fn test_can_add_child_nodes_to_an_empty_parent_node() {
            let mut node = Node::new(1);
            node.add_child(Node::new(2));
            node.add_child(Node::new(3));

            assert_eq!(node.children.len(), 2);
        }

        #[test]
        fn test_can_add_child_nodes_to_parent_node_and_read_added_child_node() {
            let mut node = Node::new(1);
            node.add_child(Node::new(2));
            node.add_child(Node::new(3));

            let x = node.get_child(&2).unwrap();
            x.borrow_mut()
                .children
                .insert(4, Rc::new(RefCell::new(Node::new(4))));

            let y = node.get_child(&2).unwrap();
            assert_eq!(y.borrow().children.len(), 1);
            assert_eq!(y.borrow().children.contains_key(&4), true);
            assert_eq!(y.borrow().children.get(&4).unwrap().borrow().key, 4);
        }
    }
}

mod qtree {

    use crate::node::Node;
    use std::cell::RefCell;
    use std::rc::Rc;

    pub fn get_char<'a>(v: &'a Vec<u8>, pos: usize) -> Option<u8> {
        if v.len() > pos {
            return Some(v[pos]);
        }
        None
    }

    pub struct Qtree {
        root: Rc<RefCell<Node>>,
        curr: Rc<RefCell<Node>>,
        node_count: u32,
        query_count: u32,
    }

    impl Qtree {
        pub fn new() -> Self {
            let root = Rc::new(RefCell::new(Node::new(0)));
            let curr = root.clone();
            Qtree {
                root,
                curr,
                node_count: 1,
                query_count: 0,
            }
        }

        pub fn node_count(&self) -> u32 {
            self.node_count
        }

        pub fn query_count(&self) -> u32 {
            self.query_count
        }

        fn reset_curr(&mut self) {
            self.curr = self.root.clone();
        }

        pub fn add(&mut self, query: String) {
            let v = query.into_bytes().to_vec();
            self.build_path(v, 0);
            self.query_count += 1;
        }

        pub fn get(&mut self, query: String) -> Vec<u8> {
            let v = query.into_bytes().to_vec();
            let mut path: Vec<u8> = Vec::new();
            self.traverse(v, &mut path);

            path
        }

        pub fn traverse<'a>(&mut self, query: Vec<u8>, path: &'a mut Vec<u8>) {
            if let Some(ch) = get_char(&query, path.len()) {
                if let Some(next) = self.curr.clone().borrow().get_child(&ch) {
                    self.curr = next.clone();
                    path.push(ch);
                    return self.traverse(query, path);
                }
            }
            self.reset_curr();
        }

        fn build_path<'a>(&mut self, query: Vec<u8>, pos: usize) {
            if let Some(ch) = get_char(&query, pos) {
                let node = Node::new(ch);
                if !self.curr.borrow().contains_child(&ch) {
                    self.curr.borrow_mut().add_child(node);
                    self.node_count += 1;
                }
                let next = self.curr.borrow().get_child(&ch).unwrap().clone();
                self.curr = next;
                return self.build_path(query, pos + 1);
            }
            self.reset_curr();
        }

        pub fn contains(&mut self, query: String) -> bool {
            let mut path = Vec::new();
            let query = query.into_bytes().to_vec();
            self.traverse(query.clone(), &mut path);
            if path == query {
                return true;
            }

            return false;
        }
    }

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        pub fn test_can_create_tree_with_initial_properties() {
            let t = Qtree::new();

            assert_eq!(t.node_count(), 1);
            assert_eq!(t.query_count(), 0);

            let root_key = t.root.borrow().key;
            let curr_key = t.curr.borrow().key;

            assert_eq!(root_key, curr_key);
        }

        #[test]
        pub fn test_can_add_query_to_tree_when_query_not_exists_in_tree() {
            let mut t = Qtree::new();
            assert_eq!(t.node_count(), 1);
            assert_eq!(t.query_count(), 0);

            t.add("foo".to_string());

            assert_eq!(t.node_count(), 4);
            assert_eq!(t.query_count(), 1);
        }

        #[test]
        pub fn test_can_get_query_from_tree_when_query_exists_in_tree() {
            let mut t = Qtree::new();
            t.add("foo".to_string());

            assert_eq!(t.node_count(), 4);
            assert_eq!(t.query_count(), 1);

            let path = t.get("foo".to_string());

            assert_eq!(path, "foo".to_string().into_bytes().to_vec());
        }

        #[test]
        pub fn test_can_add_multiple_queries_to_graph_and_only_the_marginal_difference_is_added_to_tree() {
            let mut t = Qtree::new();
            assert_eq!(t.node_count(), 1);
            assert_eq!(t.query_count(), 0);

            t.add("foo".to_string());
            t.add("bar".to_string());
            t.add("foozo".to_string());

            // (3)foo + (3)bar (2)foozo + (1)root = 9
            assert_eq!(t.node_count(), 9);
            assert_eq!(t.query_count(), 3);
        }

        #[test]
        pub fn test_contains_returns_whether_query_is_in_tree() {
            let mut t = Qtree::new();
            assert_eq!(t.node_count(), 1);
            assert_eq!(t.query_count(), 0);

            t.add("foo".to_string());
            t.add("bar".to_string());

            assert_eq!(t.contains("foo".to_string()), true);
            assert_eq!(t.contains("bar".to_string()), true);
            assert_eq!(t.contains("zoo".to_string()), false);
        }
    }
}
