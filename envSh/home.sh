#! /bin/sh
#
# home.sh
# Copyright (C) 2018 nitepone <luna@moon>
#
# Distributed under terms of the MIT license.
#

mydir=$(dirname "$0")
echo $mydir
feh --bg-center "$mydir"/wallpapers/penguin.png
cp ~/.config/termite/tomorrow-night-blue ~/.config/termite/config
