#!/bin/sh

locate_python() {
  for c in python3.9 python3.8 python3; do
    p=$(which $c)
    if [ $? -ne 0 ]; then continue; fi
    PYTHON_CMD=$(basename $p)
    return 0
  done
  echo "python3 must be in PATH"
  exit -1
}

start() {
  if [ -f $HOMEKIT_REPO/$VENV/bin/activate ]; then
    . $HOMEKIT_REPO/$VENV/bin/activate
  else
    echo "you must setup first"
    exit -1
  fi
  cd $HOMEKIT_REPO
  $PYTHON_CMD homeserver.py &
  echo $! >$PID_FILE
}

stop() {
  kill -TERM $(cat $PID_FILE)
  sleep 5
  kill -9 $(cat $PID_FILE)
  rm $PID_FILE
}

status() {
  if [ -e $PID_FILE ]; then
    echo homekitrelay is running, pid=$(cat $PID_FILE)
  else
    echo homekitrelay.sh is NOT running
    exit 1
  fi
}

setup() {
  $PYTHON_CMD -m venv $HOMEKIT_REPO/$VENV
  . $HOMEKIT_REPO/$VENV/bin/activate
  $PYTHON_CMD -m pip install --upgrade pip
  $PYTHON_CMD -m pip install --no-cache-dir -r requirements.txt
}

# main
HOMEKIT_REPO=$(dirname $0)
PID_FILE=$HOMEKIT_REPO/config/homekitrelay.pid
VENV=hapenv

case "$1" in
setup)
  locate_python
  setup
  ;;
start)
  locate_python
  start
  ;;
stop)
  stop
  ;;
restart)
  locate_python
  stop
  start
  ;;
status)
  status
  ;;
*)
  echo "Usage: $0 {start|stop|status|restart|setup}"
  ;;
esac
exit 0
