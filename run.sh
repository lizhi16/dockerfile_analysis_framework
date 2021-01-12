#!/bin/bash

ls images_list | while read file
do
	python3 main.py ./images_list/$file
done
