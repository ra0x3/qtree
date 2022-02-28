use std::cell::RefCell;
use std::rc::Rc;

use crate::node::Node;

pub struct Graph {
    root: Node,
    node_count: u32,
    query_count: u32,
    curr: Option<Rc<RefCell<Node>>>,
}

fn get_char<'a>(v: &'a Vec<u8>, pos: usize) -> Option<u8> {
    if v.len() > pos {
        return Some(v[pos]);
    }
    None
}

impl Graph {
    fn new() -> Self {
        Graph {
            root: Node::new(0),
            node_count: 0,
            query_count: 0,
            curr: None,
        }
    }

    fn get_node_count(&self) -> u32 {
        self.node_count
    }

    fn get_query_count(&self) -> u32 {
        self.query_count
    }

    fn reset_root(&mut self) {
        self.curr = Some(Rc::new(RefCell::new(Node::new(2))));
    }

    pub fn add(&mut self, query: String) {
        let v = query.as_bytes().to_vec();
        self.query_count += 1;
        self.build_path(&v, 0);
    }

    fn traverse<'a>(&mut self, query: &'a Vec<u8>, path: &'a Vec<u8>) -> Option<&'a Vec<u8>> {
        if self.curr.is_none() {
            return Some(path);
        }

        match get_char(query, path.len()) {
            Some(ch) => {
                if !self.curr.as_ref().unwrap().borrow().contains_child(&ch) {
                    return None;
                }

                let next = self.curr.as_ref().unwrap().borrow().get_child(&ch).unwrap();
                self.curr = Some(Rc::new(RefCell::new(next)));
                return self.traverse(query, path);
            }
            None => {
                self.reset_root();
                return Some(path);
            }
        }
    }

    fn build_path<'a>(&mut self, query: &'a Vec<u8>, pos: usize) {
        if let Some(curr) = &self.curr {
            match get_char(query, pos) {
                Some(ch) => {
                    let mut next = curr.borrow().get_child(&ch);
                    if next.is_none() {
                        curr.borrow_mut().add_child(Node::new(ch));
                        self.node_count += 1;
                        next = curr.borrow().get_child(&ch);
                    }
                    self.curr = Some(Rc::new(RefCell::new(next.unwrap())));
                }
                None => {
                    self.reset_root();
                }
            }
        }
    }

    pub fn includes<'a>(&mut self, query: &'a Vec<u8>) -> bool {
        self.reset_root();
        let mut v: Vec<u8> = Vec::new();
        let _ = self.traverse(query, &mut v);
        if self.curr.is_none() {
            return false;
        }
        true
    }
}

#[cfg(test)]
mod tests {
    use super::{get_char, Graph, Node};

    #[test]
    fn test_get_char_returns_char_at_index() {
        let v = vec![1, 2, 3];
        assert_eq!(Some(1), get_char(&v, 0));
    }

    #[test]
    fn test_get_char_returns_none_when_index_out_of_bounds() {
        let v = vec![1, 2, 3];
        assert_eq!(None, get_char(&v, 3));
    }

    #[test]
    fn test_can_add_query_to_graph() {
        let mut graph = Graph::new();
        graph.add("foo".to_string());

        assert_eq!(graph.query_count, 1);
        assert_eq!(graph.node_count, 3);
    }
}
