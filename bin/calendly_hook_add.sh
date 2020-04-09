#!/bin/bash

curl \
    --header "X-TOKEN: $1" \
    --data "url=http://control.meet.opencraft.com/schedule/calendly/webhook" \
    --data "events[]=invitee.created" \
    https://calendly.com/api/v1/hooks
