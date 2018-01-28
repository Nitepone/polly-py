#! /bin/sh
#
# lowbacklight.sh
# Copyright (C) 2018 nitepone <luna@moon>
#
# Distributed under terms of the MIT license.
#

mydir=$(dirname "$0")
echo $mydir
feh --bg-fill "$mydir"/wallpapers/solarized.png
cp ~/.config/termite/solarized-light ~/.config/termite/config
pkill polybar
polybar --config="$mydir"/solar -q bottom &
killall -USR1 termite
