#!/usr/bin/env python3

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Executable and reusable sample for setting a detection rule as continuous."""

import argparse
import re

import chronicle_auth
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"

RULE_ID_PATTERN = re.compile(r"ru_[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-" +
                             r"[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}")


def enable_live_rule(http_session: requests.AuthorizedSession,
                     rule_id: str) -> str:
  """Starts running a detection rule continuously.

  The rule will run against all the *new* logs that your organization has,
  shortly after they are ingested.

  There is no corresponding "disable_live_rule" action, instead you need to call
  cancel_operation() or delete_operation() with the operation ID created here.

  Args:
    http_session: Authorized session for HTTP requests.
    rule_id: Unique ID of the detection rule to run ("ru_<UUID>").

  Returns:
    Unique ID of the requested asynchronous detection operation
      ("rulejob_jo_<UUID>").

  Raises:
    ValueError: Invalid input value.
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  if not RULE_ID_PATTERN.fullmatch(rule_id):
    raise ValueError(f"Invalid detection rule ID: '{rule_id}' != 'ru_<UUID>'.")

  url = f"{CHRONICLE_API_BASE_URL}/v1/rules/{rule_id}:enableLiveRule"
  response = http_session.request("POST", url)
  # Expected server response:
  # {
  #   "name": "operations/rulejob_jo_<UUID>"
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()["name"].split("/")[1]


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  parser.add_argument(
      "-ri", "--rule_id", type=str, required=True, help="rule ID ('ru_<UUID>')")

  args = parser.parse_args()
  session = chronicle_auth.init_session(
      chronicle_auth.init_credentials(args.credentials_file))
  operation_id = enable_live_rule(session, args.rule_id)
  print(operation_id)