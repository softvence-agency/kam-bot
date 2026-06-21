#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

PID_FILE="bot.pid"
LOG_FILE="bot.log"

# activate venv
if [ -d "env" ]; then
    source env/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found."
    exit 1
fi

start() {
    echo "🚀 Starting bot in WATCH + DETACHED mode..."

    nohup watchmedo auto-restart \
        --patterns="*.py" \
        --recursive \
        -- python3 main.py \
        > "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"

    echo "✅ Bot started with PID $(cat $PID_FILE)"
    echo "📄 Logs: $LOG_FILE"
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")

        if kill -0 $PID 2>/dev/null; then
            echo "🛑 Stopping bot (PID: $PID)..."
            kill $PID
            rm "$PID_FILE"
            echo "✅ Bot stopped"
        else
            echo "⚠️ Process not running"
            rm "$PID_FILE"
        fi
    else
        echo "❌ No PID file found"
    fi
}

restart() {
    stop
    sleep 2
    start
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            echo "🟢 Bot running (PID: $PID)"
        else
            echo "🔴 Bot not running (stale PID)"
        fi
    else
        echo "⚪ Bot not running"
    fi

    if [ -f "$LOG_FILE" ]; then
        echo ""
        echo "📄 Last 10 lines of logs ($LOG_FILE):"
        tail -n 10 "$LOG_FILE"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        ;;
esac