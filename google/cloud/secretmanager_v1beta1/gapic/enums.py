# -*- coding: utf-8 -*-
#
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Wrappers for protocol buffer enum types."""

import enum


class SecretVersion(object):
    class State(enum.IntEnum):
        """
        A designation of a specific field behavior (required, output only,
        etc.) in protobuf messages.

        Examples:

        string name = 1 [(google.api.field_behavior) = REQUIRED]; State state =
        1 [(google.api.field_behavior) = OUTPUT_ONLY]; google.protobuf.Duration
        ttl = 1 [(google.api.field_behavior) = INPUT_ONLY];
        google.protobuf.Timestamp expire_time = 1 [(google.api.field_behavior) =
        OUTPUT_ONLY, (google.api.field_behavior) = IMMUTABLE];

        Attributes:
          STATE_UNSPECIFIED (int): Not specified. This value is unused and invalid.
          ENABLED (int): The ``Secret`` will only be replicated into the locations specified.
          DISABLED (int): Request message for ``SecretManagerService.CreateSecret``.
          DESTROYED (int): Response message for ``SecretManagerService.AccessSecretVersion``.
        """

        STATE_UNSPECIFIED = 0
        ENABLED = 1
        DISABLED = 2
        DESTROYED = 3
