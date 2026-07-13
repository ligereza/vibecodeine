#!/data/data/com.termux/files/usr/bin/sh
# Launch the Xiaomi controller ON the phone (Termux + Shizuku/rish backend).
# Idempotent: re-run any time to restart with fresh code copied from /sdcard.
# Prereqs (once): Shizuku service armed, rish set up in $HOME, `pip install flask`.

pkill -f 'python server.py' 2>/dev/null
sleep 1

rm -rf "$HOME/xioserver" "$HOME/xioplugins"
cp -r /sdcard/xio_termux/new "$HOME/xioserver"
cp -r /sdcard/xio_termux/new-plugins "$HOME/xioplugins"
rm -rf "$HOME/xioserver/__pycache__" "$HOME/xioserver/plugins/__pycache__" "$HOME/xioserver/data"

cd "$HOME/xioserver" || exit 1
export XIO_BACKEND=rish
export RISH_PATH="$HOME/rish"
export PLUGINS_DIR="$HOME/xioplugins"

nohup python server.py > /sdcard/xio_termux/server.log 2>&1 &
echo "launched pid $! (log: /sdcard/xio_termux/server.log)"
