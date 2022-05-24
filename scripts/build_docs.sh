#!/bin/sh
cd ../docs
rm -r source/
mkdir source
python3 generate_source_rst.py
make html