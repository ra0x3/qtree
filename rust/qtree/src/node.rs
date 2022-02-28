use std::collections::HashMap;
use std::hash::{Hash, Hasher};

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Node {
    pub key: u8,
    pub children: HashMap<u8, Node>,
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
        self.children.insert(other.key, other);
    }

    pub fn contains_child(&self, key: &u8) -> bool {
        self.children.contains_key(key)
    }

    pub fn get_child(&self, key: &u8) -> Option<Node> {
        match self.children.get(key) {
            Some(n) => {
                return Some(n.clone());
            }
            None => {
                return None;
            }
        };
    }
}

#[cfg(test)]
pub mod test {
    use super::Node;
}
