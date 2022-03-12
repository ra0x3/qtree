#![allow(dead_code)]
#![allow(unused_variables)]
#![allow(clippy::single_char_pattern)]
#![allow(clippy::needless_range_loop)]

use qtree::qtree::Qtree;
use std::collections::HashMap;
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

fn export_bench_csv(series: HashMap<String, u32>) {
    let workdir = Path::new(env!("CARGO_MANIFEST_DIR"));
    let datadir = workdir.parent().unwrap().parent().unwrap();
    let path = datadir.to_str().unwrap().to_string() + "/data/rust-bench.csv";
}

fn plot_bench() {
    let n = 100;
    let data = load_queries_txt().unwrap();

    let mut qt = Qtree::new();

    let mut actual: Vec<u32> = Vec::new();
    let mut raw: Vec<u32> = Vec::new();
    let mut nodes: Vec<u32> = Vec::new();
    let mut queries: Vec<u32> = Vec::new();

    for i in 0..n {
        let word = data[i].clone();
        qt.add(word);

        actual.push(qt.actual_size_bytes());
        raw.push(qt.raw_size_bytes());
        nodes.push(qt.node_count());
        queries.push(qt.query_count());
    }

    let mut series: HashMap<String, Vec<u32>> = HashMap::new();
    series.insert("actual".to_string(), actual);
    series.insert("raw".to_string(), raw);
    series.insert("nodes".to_string(), nodes);
    series.insert("queries".to_string(), queries);
}

fn main() {
    let x = load_queries_txt();
    println!("{:?}", x);
}
