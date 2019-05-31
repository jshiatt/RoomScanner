#!/bin/bash
cd $HOME/RoomScanner
echo "Starting Scanner"
zenity --info --timeout 3 --text "Starting Scanner..."
echo "Turning off screen blank"
xset s off
xset -dpms
xset s noblank

echo "Getting rid of cursor"
pgrep unclutter >/dev/null 2>&1
if [ $? -eq 1 ]
then
	unclutter >/dev/null 2>&1 &
fi

echo "Launching"
cd Display
python PyDisplay.py
