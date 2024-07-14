
# Overview

## Simple run, it will skip by default the folders .venv venv env .env
python app.py GeminiapiKey '/path to your folder with python codes/' '/path output folder of html documentation/' 

## Run with --skip-dirs for additional folders to skip creating documentation
python app.py GeminiapiKey '/path to your folder with python codes/' '/path output folder of html documentation/' --skip-dirs other_dir some_dir