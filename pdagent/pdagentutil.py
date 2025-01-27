#
# Python utility module for sending events to PagerDuty Integration API.
#
# Uses the PagerDuty Integration API:
# http://developer.pagerduty.com/documentation/integration/events
#
# Copyright (c) 2013-2014, PagerDuty, Inc. <info@pagerduty.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the copyright holder nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

#Checks permissions, status, builds evnt json & queue_event definition

from datetime import datetime
import json
import os
import sys
import time

from constants import MAX_DESCRIPTION_LEN

def find_in_sys_path(file_path):
    for directory in sys.path:
        abs_path = os.path.join(directory, file_path)
        if os.access(abs_path, os.R_OK):
            return abs_path
    return None


def ensure_readable_directory(d):
    if not os.access(d, os.R_OK):
        raise Exception(
            "Can't read directory %s, please check permissions" % d
            )


def ensure_writable_directory(d):
    if not os.access(d, os.W_OK):
        raise Exception(
            "Can't write to directory %s, please check permissions" % d
            )


def utcnow_isoformat(time_calc=None):
    if not time_calc:
        time_calc = time
    return time_calc.strftime("%Y-%m-%dT%H:%M:%SZ", time_calc.gmtime())

def queue_event(
        enqueuer,
        event_type, service_key, incident_key, description, client, client_url, details,
        agent_id, queued_by,
        ):
    agent_context = {
        "agent_id": agent_id,
        "queued_by": queued_by,
        "queued_at": utcnow_isoformat()
        }
    event = _build_event_json_str(
        event_type, service_key, incident_key, description, client, client_url, details,
        agent_context
        )
    _, problems = enqueuer.enqueue(service_key, event)
    return incident_key, problems


def resurrect_events(queue, service_key):
    return queue.resurrect(service_key)


def get_stats(queue, service_key):
    return queue.get_stats(
        detailed_snapshot=True,
        per_service_key_snapshot=True,
        service_key=service_key
        )


def _build_event_json_str(
    event_type, service_key, incident_key, description, client, client_url, details,
    agent_context=None
    ):
    d = {
        "service_key": service_key,
        "event_type": event_type,
        "details": details,
        }
    if incident_key is not None:
        d["incident_key"] = incident_key
    if description is not None:
        d["description"] = description[:MAX_DESCRIPTION_LEN]
    if client is not None:
        d["client"] = client
    if client_url is not None:
        d["client_url"] = client_url
    if agent_context is not None:
        d["agent"] = agent_context

    return json.dumps(
        d,
        separators=(',', ':'),  # compact json str
        sort_keys=True
        )
