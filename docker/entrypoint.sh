#! /bin/sh
set -eu

warn() {
  1>&2 echo "$@"
}

err() {
  warn "$@" && exit 1
}

MONGO_PASSWORD="$(cat "$MONGO_USER_PASSWORD_FILE")"
RABBITMQ_AMQP_PASSWORD="$(cat "${RABBITMQ_AMQP_PASSWORD_FILE}")"

export MONGO_PASSWORD RABBITMQ_AMQP_PASSWORD

if [ "$DEV_MODE" = 1 ]; then
    pip3 install --editable .[reload]
    pip3 install --editable "${SALTBOX_SDK_SRC_PATH}[mongo,event-bus]"
fi

cmd_uvicorn() {
  cmd='/usr/bin/uvicorn app.main:app'
  cmd="${cmd} --host=0.0.0.0 --port=8000"
  cmd="${cmd} --timeout-graceful-shutdown=${TIMEOUT_GRACEFUL_SHUTDOWN:-5}"
  cmd="${cmd} --workers=${UVICORN_WORKERS:-1}"
  if [ "$DEV_MODE" = 1 ]; then
    cmd="$cmd --reload"
  fi
}

cmd_shell() {
  shift
  cmd="$*"
}

wrong_cmd() {
  warn "Unknown command \"${*}\""
  err "Try \"shell ${*}\" for arbitrary command"
}

case $1 in
  uvicorn) cmd_uvicorn ;;
  shell) cmd_shell "$@" ;;
  *) wrong_cmd "$@" ;;
esac

echo "$ ${cmd}"
exec $cmd
