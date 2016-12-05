#!/bin/sh
for var in 20 21 22 23 24 25 26 27 28 29 30 31 32
do
  var=$((($var * 1000) + ( * 100))) 
  python comment_counts.py authors.txt comment_counts/comment_counts ${var} 100
done
