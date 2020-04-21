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


import google.api_core.grpc_helpers

from google.cloud.secretmanager_v1.proto import service_pb2_grpc


class SecretManagerServiceGrpcTransport(object):
    """gRPC transport class providing stubs for
    google.cloud.secretmanager.v1 SecretManagerService API.

    The transport provides access to the raw gRPC stubs,
    which can be used to take advantage of advanced
    features of gRPC.
    """

    # The scopes needed to make gRPC calls to all of the methods defined
    # in this service.
    _OAUTH_SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)

    def __init__(
        self, channel=None, credentials=None, address="secretmanager.googleapis.com:443"
    ):
        """Instantiate the transport class.

        Args:
            channel (grpc.Channel): A ``Channel`` instance through
                which to make calls. This argument is mutually exclusive
                with ``credentials``; providing both will raise an exception.
            credentials (google.auth.credentials.Credentials): The
                authorization credentials to attach to requests. These
                credentials identify this application to the service. If none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            address (str): The address where the service is hosted.
        """
        # If both `channel` and `credentials` are specified, raise an
        # exception (channels come with credentials baked in already).
        if channel is not None and credentials is not None:
            raise ValueError(
                "The `channel` and `credentials` arguments are mutually " "exclusive."
            )

        # Create the channel.
        if channel is None:
            channel = self.create_channel(
                address=address,
                credentials=credentials,
                options={
                    "grpc.max_send_message_length": -1,
                    "grpc.max_receive_message_length": -1,
                }.items(),
            )

        self._channel = channel

        # gRPC uses objects called "stubs" that are bound to the
        # channel and provide a basic method for each RPC.
        self._stubs = {
            "secret_manager_service_stub": service_pb2_grpc.SecretManagerServiceStub(
                channel
            )
        }

    @classmethod
    def create_channel(
        cls, address="secretmanager.googleapis.com:443", credentials=None, **kwargs
    ):
        """Create and return a gRPC channel object.

        Args:
            address (str): The host for the channel to use.
            credentials (~.Credentials): The
                authorization credentials to attach to requests. These
                credentials identify this application to the service. If
                none are specified, the client will attempt to ascertain
                the credentials from the environment.
            kwargs (dict): Keyword arguments, which are passed to the
                channel creation.

        Returns:
            grpc.Channel: A gRPC channel object.
        """
        return google.api_core.grpc_helpers.create_channel(
            address, credentials=credentials, scopes=cls._OAUTH_SCOPES, **kwargs
        )

    @property
    def channel(self):
        """The gRPC channel used by the transport.

        Returns:
            grpc.Channel: A gRPC channel object.
        """
        return self._channel

    @property
    def list_secrets(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.list_secrets`.

        javalite_serializable

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].ListSecrets

    @property
    def create_secret(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.create_secret`.

        Required. The resource name of the ``Secret``, in the format
        ``projects/*/secrets/*``.

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].CreateSecret

    @property
    def add_secret_version(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.add_secret_version`.

        Returns permissions that a caller has on the specified resource. If
        the resource does not exist, this will return an empty set of
        permissions, not a NOT_FOUND error.

        Note: This operation is designed to be used for building
        permission-aware UIs and command-line tools, not for authorization
        checking. This operation may "fail open" without warning.

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].AddSecretVersion

    @property
    def get_secret(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.get_secret`.

        The ``SecretVersion`` may not be accessed, but the secret data is
        still available and can be placed back into the ``ENABLED`` state.

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].GetSecret

    @property
    def update_secret(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.update_secret`.

        An annotation that describes a resource definition without a
        corresponding message; see ``ResourceDescriptor``.

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].UpdateSecret

    @property
    def delete_secret(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.delete_secret`.

        Accesses a ``SecretVersion``. This call returns the secret data.

        ``projects/*/secrets/*/versions/latest`` is an alias to the ``latest``
        ``SecretVersion``.

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].DeleteSecret

    @property
    def list_secret_versions(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.list_secret_versions`.

        The ``SecretVersion`` is destroyed and the secret data is no longer
        stored. A version may not leave this state once entered.

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].ListSecretVersions

    @property
    def get_secret_version(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.get_secret_version`.

        Identifies which part of the FileDescriptorProto was defined at this
        location.

        Each element is a field number or an index. They form a path from the
        root FileDescriptorProto to the place where the definition. For example,
        this path: [ 4, 3, 2, 7, 1 ] refers to: file.message_type(3) // 4, 3
        .field(7) // 2, 7 .name() // 1 This is because
        FileDescriptorProto.message_type has field number 4: repeated
        DescriptorProto message_type = 4; and DescriptorProto.field has field
        number 2: repeated FieldDescriptorProto field = 2; and
        FieldDescriptorProto.name has field number 1: optional string name = 1;

        Thus, the above path gives the location of a field name. If we removed
        the last element: [ 4, 3, 2, 7 ] this path refers to the whole field
        declaration (from the beginning of the label to the terminating
        semicolon).

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].GetSecretVersion

    @property
    def access_secret_version(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.access_secret_version`.

        Specifies a service that was configured for Cloud Audit Logging. For
        example, ``storage.googleapis.com``, ``cloudsql.googleapis.com``.
        ``allServices`` is a special value that covers all services. Required

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].AccessSecretVersion

    @property
    def disable_secret_version(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.disable_secret_version`.

        Request message for ``SecretManagerService.ListSecretVersions``.

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].DisableSecretVersion

    @property
    def enable_secret_version(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.enable_secret_version`.

        Output only. The resource name of the ``SecretVersion`` in the
        format ``projects/*/secrets/*/versions/*``.

        ``SecretVersion`` IDs in a ``Secret`` start at 1 and are incremented for
        each subsequent version of the secret.

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].EnableSecretVersion

    @property
    def destroy_secret_version(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.destroy_secret_version`.

        Protocol Buffers - Google's data interchange format Copyright 2008
        Google Inc. All rights reserved.
        https://developers.google.com/protocol-buffers/

        Redistribution and use in source and binary forms, with or without
        modification, are permitted provided that the following conditions are
        met:

        ::

            * Redistributions of source code must retain the above copyright

        notice, this list of conditions and the following disclaimer. \*
        Redistributions in binary form must reproduce the above copyright
        notice, this list of conditions and the following disclaimer in the
        documentation and/or other materials provided with the distribution. \*
        Neither the name of Google Inc. nor the names of its contributors may be
        used to endorse or promote products derived from this software without
        specific prior written permission.

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
        IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
        TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
        PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
        OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
        EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
        PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
        PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
        LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
        NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
        SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].DestroySecretVersion

    @property
    def set_iam_policy(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.set_iam_policy`.

        Required. The resource name of the ``Secret`` associated with the
        ``SecretVersions`` to list, in the format ``projects/*/secrets/*``.

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].SetIamPolicy

    @property
    def get_iam_policy(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.get_iam_policy`.

        Gets the access control policy for a secret.
        Returns empty policy if the secret exists and does not have a policy set.

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].GetIamPolicy

    @property
    def test_iam_permissions(self):
        """Return the gRPC stub for :meth:`SecretManagerServiceClient.test_iam_permissions`.

        An annotation that describes a resource definition, see
        ``ResourceDescriptor``.

        Returns:
            Callable: A callable which accepts the appropriate
                deserialized request object and returns a
                deserialized response object.
        """
        return self._stubs["secret_manager_service_stub"].TestIamPermissions
