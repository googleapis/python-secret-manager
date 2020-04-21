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
        The hostname for this service. This should be specified with no
        prefix or protocol.

        Example:

        service Foo { option (google.api.default_host) = "foo.googleapi.com";
        ... }

        Attributes:
          STATE_UNSPECIFIED (int): Not specified. This value is unused and invalid.
          ENABLED (int): Request message for ``SecretManagerService.CreateSecret``.
          DISABLED (int): A ``Secret`` is a logical secret whose value and versions can be
          accessed.

          A ``Secret`` is made up of zero or more ``SecretVersions`` that
          represent the secret data.
          DESTROYED (int): Required. The resource name of the ``Secret`` to delete in the
          format ``projects/*/secrets/*``.
        """

        STATE_UNSPECIFIED = 0
        ENABLED = 1
        DISABLED = 2
        DESTROYED = 3
