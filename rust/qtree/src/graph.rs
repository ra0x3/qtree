use crate::node::Node;

pub struct Graph {
    root: Option<Node>,
    curr: Option<Node>,
}

impl Graph {
    pub fn set_root(&mut self, node: Node) {
        self.root = Some(node);
    }

    fn _build_path(&mut self, query: String, pos: usize, curr: Option<Node>) {
    }
}

#[cfg(test)]
mod tests {
    use super::Graph;
    fn test_can_init_graph() {}
}
