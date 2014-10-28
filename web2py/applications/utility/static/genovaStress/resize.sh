#!/bin/bash
# convert rose.jpg -resize 50% rose.jpg
# identify -format "%[fx:w]x%[fx:h]" image.jpg

IMAGES=`ls *.jpg`

for IMAGE in $IMAGES
do
	IMAGE_SIZE=`identify -format "%[fx:w]x%[fx:h]" $IMAGE`	
	IMAGE_WIDTH=${IMAGE_SIZE%x*}
	SMALL=$(( $IMAGE_WIDTH < 500 ))
	if [ $SMALL = 0 ]
	then
		echo $IMAGE
		echo $IMAGE_WIDTH
		echo "This is a large image"
		convert $IMAGE -resize 50% $IMAGE
		identify -format "%[fx:w]x%[fx:h]" $IMAGE
	fi
done



