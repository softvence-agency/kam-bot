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
    echo "📦 Syncing packages..."
    pip install -r requirements.txt
    
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
        echo "--- 📊 BOT STATISTICS ---"
        python3 -c "
import sys, datetime

total_req = 0
success_req = 0
errors = 0
start_time = None

try:
    with open('$LOG_FILE', 'r') as f:
        for line in f:
            if 'Bot is running' in line and not start_time:
                ts = line.split(' - ')[0]
                try:
                    start_time = datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S,%f')
                except Exception:
                    pass
            if 'HTTP Request:' in line:
                total_req += 1
                if '200 OK' in line or 'HTTP/2 200' in line:
                    success_req += 1
            if ' - ERROR - ' in line or 'Traceback' in line or 'Exception' in line:
                errors += 1

    if start_time:
        uptime = datetime.datetime.now() - start_time
        print(f'⏱️  Uptime: {str(uptime).split(\".\")[0]} (Started: {start_time.strftime(\"%Y-%m-%d %H:%M:%S\")})')
    else:
        print('⏱️  Uptime: Unknown')

    failed_req = total_req - success_req
    rate = (success_req / total_req * 100) if total_req > 0 else 0
    print(f'🌍 API Requests: {total_req} Total | ✅ {success_req} Success | ❌ {failed_req} Failed')
    print(f'⚠️  App Errors: {errors}')
    print(f'📈 API Success Rate: {rate:.2f}%')

except Exception as e:
    print('Stats unavailable')
"
        echo "-------------------------"
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
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        ;;
esac