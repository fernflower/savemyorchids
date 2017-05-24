#!/bin/sh

# XXX FIXME a temporary solution, figure out how to make it 
# nicer
CLONE_DEST="/tmp/rpi_ws281x"
GITHUB_LINK="https://github.com/fernflower/rpi_ws281x"
DIR="/root/savemyorchids/"

git clone "$GITHUB_LINK" $CLONE_DEST
apt-get install python-dev swig scons
echo "Building c driver.."
cd "$CLONE_DEST" && scons
echo "Building python bindings.."
cd "$CLONE_DEST/python" && python setup.py build
cp -r "$CLONE_DEST/python/build" "$DIR"
# rm -r "$CLONE_DEST"
