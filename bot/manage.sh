#!/bin/bash
# BKNS Wiki Bot — Start/Stop/Status/Restart
# Usage: ./bot/manage.sh start|stop|status|restart

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/bot/.wiki_bot.pid"
LOG_FILE="$PROJECT_DIR/logs/wiki-bot.log"

export PYTHONPATH="$PROJECT_DIR"

start() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Bot already running (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    echo "Starting BKNS Wiki Bot..."
    cd "$PROJECT_DIR"
    nohup python3 bot/wiki_bot.py --daemon >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "✅ Started (PID: $!)"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "No PID file found. Bot may not be running."
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        rm "$PID_FILE"
        echo "✅ Bot stopped (PID: $PID)"
    else
        rm "$PID_FILE"
        echo "PID $PID not running. Cleaned up PID file."
    fi
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "✅ Running (PID: $(cat $PID_FILE))"
        echo "Log: tail -f $LOG_FILE"
    else
        echo "❌ Not running"
    fi
}

restart() {
    stop
    sleep 1
    start
}

case "${1}" in
    start)   start ;;
    stop)    stop ;;
    status)  status ;;
    restart) restart ;;
    *)       echo "Usage: $0 {start|stop|status|restart}" ;;
esac
