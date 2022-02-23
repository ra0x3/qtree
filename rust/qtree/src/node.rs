#[derive(Clone, Debug, Eq, PartialEq)]

pub struct Node {
    bin: String,
    left: Box<Option<Node>>,
    right: Box<Option<Node>>,
}

pub fn to_binary_str(x: String) -> String {
    let mut result = "".to_string();
    for ch in x.clone().as_bytes() {
        result += &format!("{:b}", ch);
    }
    result
}

impl Node {
    pub fn new(query: String) -> Self {
        Node {
            bin: to_binary_str(query),
            left: Box::new(None),
            right: Box::new(None),
        }
    }

    pub fn len(&self) -> usize {
        self.bin.len()
    }

    pub fn add_child(&mut self, node: Self) {
        let binbytes = node.bin.as_bytes();
        if binbytes[binbytes.len() - 1] == b'1' {
            self.right = Box::new(Some(node));
        } else {
            self.left = Box::new(Some(node));
        }
    }

    pub fn is_leaf(self) -> bool {
        *self.right == None && *self.left == None
    }
}

#[cfg(test)]
pub mod test {
    use super::{to_binary_str, Node};

    #[test]
    fn test_to_binary_str_returns_binary_str_of_str() {
        let result = to_binary_str("abc".to_string());
        assert_eq!(result, "110000111000101100011".to_string());
    }

    #[test]
    fn test_can_create_new_node_with_empty_children() {
        let node = Node::new("foo".to_string());
        assert_eq!(node.bin, "110011011011111101111".to_string());
        assert_eq!(*node.left, None);
        assert_eq!(*node.right, None);
    }

    #[test]
    fn test_node_add_child_adds_child_node_to_proper_place() {
        let mut node = Node::new("foo".to_string());
        let child = Node::new("bar".to_string());
        let child_clone = child.clone();
        node.add_child(child);
        assert_eq!(*node.left, Some(child_clone));
        assert_eq!(*node.right, None);
    }

    #[test]
    fn test_len_returns_size_of_binary_str() {
        let node = Node::new("foo".to_string());
        assert_eq!(node.len(), 21);
    }
}
