#!/bin/bash
git stash
git pull
git stash pop
git add chat_database.txt
git add broadcast_database.txt
git add --all broadcast_files/
git commit -m "Backed up ID database"
git push origin master
lxterminal -e 'source env/bin/activate ; python main_script.py' &
