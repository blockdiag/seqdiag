#!/bin/sh
sudo add-apt-repository ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install python2.6 python2.6-dev python3.4 python3.4-dev fonts-ipafont-gothic fonts-vlgothic libjpeg8-dev libfreetype6-dev

mkdir src/seqdiag/tests/truetype
cp /usr/share/fonts/truetype/vlgothic/VL-PGothic-Regular.ttf src/seqdiag/tests/truetype

pip install --use-mirrors --upgrade detox misspellings check-manifest docutils
find src/ -name "*.py" | misspellings -f -
detox
check-manifest
