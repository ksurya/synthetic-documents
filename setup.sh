#!/usr/bin/env bash

mkdir data

# load google fonts
git clone https://github.com/google/fonts.git data/fonts/

# load datasets
mkdir data/squad
wget https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v2.0.json -O data/squad/train-v2.0.json
wget https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v2.0.json -O data/squad/dev-v2.0.json
