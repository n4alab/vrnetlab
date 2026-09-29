VENDOR=N4ALab
NAME=Flinos
IMAGE_FORMAT=qcow2
IMAGE_GLOB=flinos-*-amd64.qcow2

# Example: flinos-0.1.0-dev.42-amd64.qcow2 -> 0.1.0-dev.42-amd64
VERSION=$(shell echo $(IMAGE) | sed -E 's/^flinos-(.+)\.qcow2$$/\1/')

-include ../../makefile-sanity.include
-include ../../makefile.include
