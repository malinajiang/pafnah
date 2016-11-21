#!/bin/sh
for var in 14 15 16 17 18 19
do
	var=$(($var * 1000)) 
  python comment_counts.py authors.txt comment_counts/comment_counts ${var} 1000
done