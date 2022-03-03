use qtree::node::Node;
use qtree::qtree::Qtree;
use std::io::{prelude::*, BufReader, Error};
use std::path::Path;

fn load_queries_txt() -> Result<Vec<String>, Error> {
    let workdir = Path::new(env!("CARGO_MANIFEST_DIR"));
    let datadir = workdir.parent().unwrap().parent().unwrap();
    let path = datadir.to_str().unwrap().to_string() + "/data/queries.txt";

    let file = std::fs::File::open(path)?;
    let reader = BufReader::new(file);

    let mut queries: Vec<String> = Vec::new();
    for line in reader.lines() {
        let words: Vec<String> = line
            .unwrap()
            .split(" ")
            .collect::<Vec<&str>>()
            .iter()
            .map(|word| word.to_string())
            .collect();
        for word in words {
            queries.push(word);
        }
    }

    Ok(queries)
}

fn plot_bench() {
    let n = 100;
    let data = load_queries_txt().unwrap();

    let range = 0..n;
}

fn main() {
    let x = load_queries_txt();
    println!("{:?}", x);
}
