#!/bin/bash

for IMAGE_ID in {1..575}
do
	convert -size 300x300 xc: +noise Random noise-${IMAGE_ID}.png
done
