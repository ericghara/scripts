#!/bin/sh

# Quickly fetches and runs prime95
# Also copies over a necissary lib to /usr/lib64
# Intended to be used with a knoppix live USB to quickly check system stability w/o mounting disks

echo "* Creating Directory" ~/prime95
mkdir ~/prime95
echo "* Fetching prime95 and extracting"
wget -qO- http://www.mersenne.org/ftp_root/gimps/p95v308b17.linux64.tar.gz | tar xvz -C ~/prime95/
echo "* Creating symlink for libgmp.so"
sudo ln -sf ~/prime95/libgmp.so /usr/lib64/libgmp.so.10
echo "* Starting prime95"
~/prime95/mprime
