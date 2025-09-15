#!/bin/sh

if [ "$SEPARATE_HEALTH_APP" = "1" ]; then
    export LITELLM_ARGS="$@"
    exec supervisord -c /etc/supervisord.conf
fi

if [ "$USE_DDTRACE" = "true" ]; then
    export DD_TRACE_OPENAI_ENABLED="False"
    exec ddtrace-run litellm --use_prisma_db_push "$@"
else
    exec litellm --use_prisma_db_push "$@"
fi