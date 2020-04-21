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

"""Accesses the google.cloud.secretmanager.v1 SecretManagerService API."""

import functools
import pkg_resources
import warnings

from google.oauth2 import service_account
import google.api_core.client_options
import google.api_core.gapic_v1.client_info
import google.api_core.gapic_v1.config
import google.api_core.gapic_v1.method
import google.api_core.gapic_v1.routing_header
import google.api_core.grpc_helpers
import google.api_core.page_iterator
import google.api_core.path_template
import grpc

from google.cloud.secretmanager_v1.gapic import enums
from google.cloud.secretmanager_v1.gapic import secret_manager_service_client_config
from google.cloud.secretmanager_v1.gapic.transports import (
    secret_manager_service_grpc_transport,
)
from google.cloud.secretmanager_v1.proto import resources_pb2
from google.cloud.secretmanager_v1.proto import service_pb2
from google.cloud.secretmanager_v1.proto import service_pb2_grpc
from google.iam.v1 import iam_policy_pb2
from google.iam.v1 import options_pb2
from google.iam.v1 import policy_pb2
from google.protobuf import empty_pb2
from google.protobuf import field_mask_pb2


_GAPIC_LIBRARY_VERSION = pkg_resources.get_distribution(
    "google-cloud-secret-manager"
).version


class SecretManagerServiceClient(object):
    """
    An annotation that describes a resource reference, see
    ``ResourceReference``.
    """

    SERVICE_ADDRESS = "secretmanager.googleapis.com:443"
    """The default address of the service."""

    # The name of the interface for this client. This is the key used to
    # find the method configuration in the client_config dictionary.
    _INTERFACE_NAME = "google.cloud.secretmanager.v1.SecretManagerService"

    @classmethod
    def from_service_account_file(cls, filename, *args, **kwargs):
        """Creates an instance of this client using the provided credentials
        file.

        Args:
            filename (str): The path to the service account private key json
                file.
            args: Additional arguments to pass to the constructor.
            kwargs: Additional arguments to pass to the constructor.

        Returns:
            SecretManagerServiceClient: The constructed client.
        """
        credentials = service_account.Credentials.from_service_account_file(filename)
        kwargs["credentials"] = credentials
        return cls(*args, **kwargs)

    from_service_account_json = from_service_account_file

    @classmethod
    def project_path(cls, project):
        """Return a fully-qualified project string."""
        return google.api_core.path_template.expand(
            "projects/{project}", project=project
        )

    @classmethod
    def secret_path(cls, project, secret):
        """Return a fully-qualified secret string."""
        return google.api_core.path_template.expand(
            "projects/{project}/secrets/{secret}", project=project, secret=secret
        )

    @classmethod
    def secret_version_path(cls, project, secret, secret_version):
        """Return a fully-qualified secret_version string."""
        return google.api_core.path_template.expand(
            "projects/{project}/secrets/{secret}/versions/{secret_version}",
            project=project,
            secret=secret,
            secret_version=secret_version,
        )

    def __init__(
        self,
        transport=None,
        channel=None,
        credentials=None,
        client_config=None,
        client_info=None,
        client_options=None,
    ):
        """Constructor.

        Args:
            transport (Union[~.SecretManagerServiceGrpcTransport,
                    Callable[[~.Credentials, type], ~.SecretManagerServiceGrpcTransport]): A transport
                instance, responsible for actually making the API calls.
                The default transport uses the gRPC protocol.
                This argument may also be a callable which returns a
                transport instance. Callables will be sent the credentials
                as the first argument and the default transport class as
                the second argument.
            channel (grpc.Channel): DEPRECATED. A ``Channel`` instance
                through which to make calls. This argument is mutually exclusive
                with ``credentials``; providing both will raise an exception.
            credentials (google.auth.credentials.Credentials): The
                authorization credentials to attach to requests. These
                credentials identify this application to the service. If none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
                This argument is mutually exclusive with providing a
                transport instance to ``transport``; doing so will raise
                an exception.
            client_config (dict): DEPRECATED. A dictionary of call options for
                each method. If not specified, the default configuration is used.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you're developing
                your own client library.
            client_options (Union[dict, google.api_core.client_options.ClientOptions]):
                Client options used to set user options on the client. API Endpoint
                should be set through client_options.
        """
        # Raise deprecation warnings for things we want to go away.
        if client_config is not None:
            warnings.warn(
                "The `client_config` argument is deprecated.",
                PendingDeprecationWarning,
                stacklevel=2,
            )
        else:
            client_config = secret_manager_service_client_config.config

        if channel:
            warnings.warn(
                "The `channel` argument is deprecated; use " "`transport` instead.",
                PendingDeprecationWarning,
                stacklevel=2,
            )

        api_endpoint = self.SERVICE_ADDRESS
        if client_options:
            if type(client_options) == dict:
                client_options = google.api_core.client_options.from_dict(
                    client_options
                )
            if client_options.api_endpoint:
                api_endpoint = client_options.api_endpoint

        # Instantiate the transport.
        # The transport is responsible for handling serialization and
        # deserialization and actually sending data to the service.
        if transport:
            if callable(transport):
                self.transport = transport(
                    credentials=credentials,
                    default_class=secret_manager_service_grpc_transport.SecretManagerServiceGrpcTransport,
                    address=api_endpoint,
                )
            else:
                if credentials:
                    raise ValueError(
                        "Received both a transport instance and "
                        "credentials; these are mutually exclusive."
                    )
                self.transport = transport
        else:
            self.transport = secret_manager_service_grpc_transport.SecretManagerServiceGrpcTransport(
                address=api_endpoint, channel=channel, credentials=credentials
            )

        if client_info is None:
            client_info = google.api_core.gapic_v1.client_info.ClientInfo(
                gapic_version=_GAPIC_LIBRARY_VERSION
            )
        else:
            client_info.gapic_version = _GAPIC_LIBRARY_VERSION
        self._client_info = client_info

        # Parse out the default settings for retry and timeout for each RPC
        # from the client configuration.
        # (Ordinarily, these are the defaults specified in the `*_config.py`
        # file next to this one.)
        self._method_configs = google.api_core.gapic_v1.config.parse_method_configs(
            client_config["interfaces"][self._INTERFACE_NAME]
        )

        # Save a dictionary of cached API call functions.
        # These are the actual callables which invoke the proper
        # transport methods, wrapped with `wrap_method` to add retry,
        # timeout, and the like.
        self._inner_api_calls = {}

    # Service calls
    def list_secrets(
        self,
        parent,
        page_size=None,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
        javalite_serializable

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> parent = client.project_path('[PROJECT]')
            >>>
            >>> # Iterate over all results
            >>> for element in client.list_secrets(parent):
            ...     # process element
            ...     pass
            >>>
            >>>
            >>> # Alternatively:
            >>>
            >>> # Iterate over results one page at a time
            >>> for page in client.list_secrets(parent).pages:
            ...     for element in page:
            ...         # process element
            ...         pass

        Args:
            parent (str): Response message for ``SecretManagerService.AccessSecretVersion``.
            page_size (int): The maximum number of resources contained in the
                underlying API response. If page streaming is performed per-
                resource, this parameter does not affect the return value. If page
                streaming is performed per-page, this determines the maximum number
                of resources in a page.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.api_core.page_iterator.PageIterator` instance.
            An iterable of :class:`~google.cloud.secretmanager_v1.types.Secret` instances.
            You can also iterate over the pages of the response
            using its `pages` property.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "list_secrets" not in self._inner_api_calls:
            self._inner_api_calls[
                "list_secrets"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.list_secrets,
                default_retry=self._method_configs["ListSecrets"].retry,
                default_timeout=self._method_configs["ListSecrets"].timeout,
                client_info=self._client_info,
            )

        request = service_pb2.ListSecretsRequest(parent=parent, page_size=page_size)
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("parent", parent)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        iterator = google.api_core.page_iterator.GRPCIterator(
            client=None,
            method=functools.partial(
                self._inner_api_calls["list_secrets"],
                retry=retry,
                timeout=timeout,
                metadata=metadata,
            ),
            request=request,
            items_field="secrets",
            request_token_field="page_token",
            response_token_field="next_page_token",
        )
        return iterator

    def create_secret(
        self,
        parent,
        secret_id,
        secret,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
        Required. The resource name of the ``Secret``, in the format
        ``projects/*/secrets/*``.

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> parent = client.project_path('[PROJECT]')
            >>>
            >>> # TODO: Initialize `secret_id`:
            >>> secret_id = ''
            >>>
            >>> # TODO: Initialize `secret`:
            >>> secret = {}
            >>>
            >>> response = client.create_secret(parent, secret_id, secret)

        Args:
            parent (str): Request message for ``SecretManagerService.ListSecrets``.
            secret_id (str): If this SourceCodeInfo represents a complete declaration, these are
                any comments appearing before and after the declaration which appear to
                be attached to the declaration.

                A series of line comments appearing on consecutive lines, with no other
                tokens appearing on those lines, will be treated as a single comment.

                leading_detached_comments will keep paragraphs of comments that appear
                before (but not connected to) the current element. Each paragraph,
                separated by empty lines, will be one comment element in the repeated
                field.

                Only the comment content is provided; comment markers (e.g. //) are
                stripped out. For block comments, leading whitespace and an asterisk
                will be stripped from the beginning of each line other than the first.
                Newlines are included in the output.

                Examples:

                optional int32 foo = 1; // Comment attached to foo. // Comment attached
                to bar. optional int32 bar = 2;

                optional string baz = 3; // Comment attached to baz. // Another line
                attached to baz.

                // Comment attached to qux. // // Another line attached to qux. optional
                double qux = 4;

                // Detached comment for corge. This is not leading or trailing comments
                // to qux or corge because there are blank lines separating it from //
                both.

                // Detached comment for corge paragraph 2.

                optional string corge = 5; /\* Block comment attached \* to corge.
                Leading asterisks \* will be removed. */ /* Block comment attached to \*
                grault. \*/ optional int32 grault = 6;

                // ignored detached comments.
            secret (Union[dict, ~google.cloud.secretmanager_v1.types.Secret]): Enables a ``SecretVersion``.

                Sets the ``state`` of the ``SecretVersion`` to ``ENABLED``.

                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.secretmanager_v1.types.Secret`
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.secretmanager_v1.types.Secret` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "create_secret" not in self._inner_api_calls:
            self._inner_api_calls[
                "create_secret"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.create_secret,
                default_retry=self._method_configs["CreateSecret"].retry,
                default_timeout=self._method_configs["CreateSecret"].timeout,
                client_info=self._client_info,
            )

        request = service_pb2.CreateSecretRequest(
            parent=parent, secret_id=secret_id, secret=secret
        )
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("parent", parent)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        return self._inner_api_calls["create_secret"](
            request, retry=retry, timeout=timeout, metadata=metadata
        )

    def add_secret_version(
        self,
        parent,
        payload,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
        Returns permissions that a caller has on the specified resource. If
        the resource does not exist, this will return an empty set of
        permissions, not a NOT_FOUND error.

        Note: This operation is designed to be used for building
        permission-aware UIs and command-line tools, not for authorization
        checking. This operation may "fail open" without warning.

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> parent = client.secret_path('[PROJECT]', '[SECRET]')
            >>>
            >>> # TODO: Initialize `payload`:
            >>> payload = {}
            >>>
            >>> response = client.add_secret_version(parent, payload)

        Args:
            parent (str): Secret Manager Service

                Manages secrets and operations using those secrets. Implements a REST
                model with the following objects:

                -  ``Secret``
                -  ``SecretVersion``
            payload (Union[dict, ~google.cloud.secretmanager_v1.types.SecretPayload]): Optional. Pagination token, returned earlier via
                ListSecretVersionsResponse.next_page_token][].

                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.secretmanager_v1.types.SecretPayload`
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.secretmanager_v1.types.SecretVersion` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "add_secret_version" not in self._inner_api_calls:
            self._inner_api_calls[
                "add_secret_version"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.add_secret_version,
                default_retry=self._method_configs["AddSecretVersion"].retry,
                default_timeout=self._method_configs["AddSecretVersion"].timeout,
                client_info=self._client_info,
            )

        request = service_pb2.AddSecretVersionRequest(parent=parent, payload=payload)
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("parent", parent)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        return self._inner_api_calls["add_secret_version"](
            request, retry=retry, timeout=timeout, metadata=metadata
        )

    def get_secret(
        self,
        name,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
        The ``SecretVersion`` may not be accessed, but the secret data is
        still available and can be placed back into the ``ENABLED`` state.

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> name = client.secret_path('[PROJECT]', '[SECRET]')
            >>>
            >>> response = client.get_secret(name)

        Args:
            name (str): A Location identifies a piece of source code in a .proto file which
                corresponds to a particular definition. This information is intended to
                be useful to IDEs, code indexers, documentation generators, and similar
                tools.

                For example, say we have a file like: message Foo { optional string foo
                = 1; } Let's look at just the field definition: optional string foo = 1;
                ^ ^^ ^^ ^ ^^^ a bc de f ghi We have the following locations: span path
                represents [a,i) [ 4, 0, 2, 0 ] The whole field definition. [a,b) [ 4,
                0, 2, 0, 4 ] The label (optional). [c,d) [ 4, 0, 2, 0, 5 ] The type
                (string). [e,f) [ 4, 0, 2, 0, 1 ] The name (foo). [g,h) [ 4, 0, 2, 0, 3
                ] The number (1).

                Notes:

                -  A location may refer to a repeated field itself (i.e. not to any
                   particular index within it). This is used whenever a set of elements
                   are logically enclosed in a single code segment. For example, an
                   entire extend block (possibly containing multiple extension
                   definitions) will have an outer location whose path refers to the
                   "extensions" repeated field without an index.
                -  Multiple locations may have the same path. This happens when a single
                   logical declaration is spread out across multiple places. The most
                   obvious example is the "extend" block again -- there may be multiple
                   extend blocks in the same scope, each of which will have the same
                   path.
                -  A location's span is not always a subset of its parent's span. For
                   example, the "extendee" of an extension declaration appears at the
                   beginning of the "extend" block and is shared by all extensions
                   within the block.
                -  Just because a location's span is a subset of some other location's
                   span does not mean that it is a descendant. For example, a "group"
                   defines both a type and a field in a single declaration. Thus, the
                   locations corresponding to the type and field and their components
                   will overlap.
                -  Code which tries to interpret locations should probably be designed
                   to ignore those that it doesn't understand, as more types of
                   locations could be recorded in the future.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.secretmanager_v1.types.Secret` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "get_secret" not in self._inner_api_calls:
            self._inner_api_calls[
                "get_secret"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.get_secret,
                default_retry=self._method_configs["GetSecret"].retry,
                default_timeout=self._method_configs["GetSecret"].timeout,
                client_info=self._client_info,
            )

        request = service_pb2.GetSecretRequest(name=name)
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("name", name)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        return self._inner_api_calls["get_secret"](
            request, retry=retry, timeout=timeout, metadata=metadata
        )

    def update_secret(
        self,
        secret,
        update_mask,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
        An annotation that describes a resource definition without a
        corresponding message; see ``ResourceDescriptor``.

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> # TODO: Initialize `secret`:
            >>> secret = {}
            >>>
            >>> # TODO: Initialize `update_mask`:
            >>> update_mask = {}
            >>>
            >>> response = client.update_secret(secret, update_mask)

        Args:
            secret (Union[dict, ~google.cloud.secretmanager_v1.types.Secret]): Request message for ``SecretManagerService.DeleteSecret``.

                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.secretmanager_v1.types.Secret`
            update_mask (Union[dict, ~google.cloud.secretmanager_v1.types.FieldMask]): Required. Specifies the fields to be updated.

                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.secretmanager_v1.types.FieldMask`
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.secretmanager_v1.types.Secret` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "update_secret" not in self._inner_api_calls:
            self._inner_api_calls[
                "update_secret"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.update_secret,
                default_retry=self._method_configs["UpdateSecret"].retry,
                default_timeout=self._method_configs["UpdateSecret"].timeout,
                client_info=self._client_info,
            )

        request = service_pb2.UpdateSecretRequest(
            secret=secret, update_mask=update_mask
        )
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("secret.name", secret.name)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        return self._inner_api_calls["update_secret"](
            request, retry=retry, timeout=timeout, metadata=metadata
        )

    def delete_secret(
        self,
        name,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
        Accesses a ``SecretVersion``. This call returns the secret data.

        ``projects/*/secrets/*/versions/latest`` is an alias to the ``latest``
        ``SecretVersion``.

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> name = client.secret_path('[PROJECT]', '[SECRET]')
            >>>
            >>> client.delete_secret(name)

        Args:
            name (str): The total number of ``SecretVersions``.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "delete_secret" not in self._inner_api_calls:
            self._inner_api_calls[
                "delete_secret"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.delete_secret,
                default_retry=self._method_configs["DeleteSecret"].retry,
                default_timeout=self._method_configs["DeleteSecret"].timeout,
                client_info=self._client_info,
            )

        request = service_pb2.DeleteSecretRequest(name=name)
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("name", name)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        self._inner_api_calls["delete_secret"](
            request, retry=retry, timeout=timeout, metadata=metadata
        )

    def list_secret_versions(
        self,
        parent,
        page_size=None,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
        The ``SecretVersion`` is destroyed and the secret data is no longer
        stored. A version may not leave this state once entered.

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> parent = client.secret_path('[PROJECT]', '[SECRET]')
            >>>
            >>> # Iterate over all results
            >>> for element in client.list_secret_versions(parent):
            ...     # process element
            ...     pass
            >>>
            >>>
            >>> # Alternatively:
            >>>
            >>> # Iterate over results one page at a time
            >>> for page in client.list_secret_versions(parent).pages:
            ...     for element in page:
            ...         # process element
            ...         pass

        Args:
            parent (str): The resource has one pattern, but the API owner expects to add more
                later. (This is the inverse of ORIGINALLY_SINGLE_PATTERN, and prevents
                that from being necessary once there are multiple patterns.)
            page_size (int): The maximum number of resources contained in the
                underlying API response. If page streaming is performed per-
                resource, this parameter does not affect the return value. If page
                streaming is performed per-page, this determines the maximum number
                of resources in a page.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.api_core.page_iterator.PageIterator` instance.
            An iterable of :class:`~google.cloud.secretmanager_v1.types.SecretVersion` instances.
            You can also iterate over the pages of the response
            using its `pages` property.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "list_secret_versions" not in self._inner_api_calls:
            self._inner_api_calls[
                "list_secret_versions"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.list_secret_versions,
                default_retry=self._method_configs["ListSecretVersions"].retry,
                default_timeout=self._method_configs["ListSecretVersions"].timeout,
                client_info=self._client_info,
            )

        request = service_pb2.ListSecretVersionsRequest(
            parent=parent, page_size=page_size
        )
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("parent", parent)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        iterator = google.api_core.page_iterator.GRPCIterator(
            client=None,
            method=functools.partial(
                self._inner_api_calls["list_secret_versions"],
                retry=retry,
                timeout=timeout,
                metadata=metadata,
            ),
            request=request,
            items_field="versions",
            request_token_field="page_token",
            response_token_field="next_page_token",
        )
        return iterator

    def get_secret_version(
        self,
        name,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
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

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> name = client.secret_version_path('[PROJECT]', '[SECRET]', '[SECRET_VERSION]')
            >>>
            >>> response = client.get_secret_version(name)

        Args:
            name (str): A token to retrieve the next page of results. Pass this value in
                ``ListSecretsRequest.page_token`` to retrieve the next page.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.secretmanager_v1.types.SecretVersion` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "get_secret_version" not in self._inner_api_calls:
            self._inner_api_calls[
                "get_secret_version"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.get_secret_version,
                default_retry=self._method_configs["GetSecretVersion"].retry,
                default_timeout=self._method_configs["GetSecretVersion"].timeout,
                client_info=self._client_info,
            )

        request = service_pb2.GetSecretVersionRequest(name=name)
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("name", name)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        return self._inner_api_calls["get_secret_version"](
            request, retry=retry, timeout=timeout, metadata=metadata
        )

    def access_secret_version(
        self,
        name,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
        Specifies a service that was configured for Cloud Audit Logging. For
        example, ``storage.googleapis.com``, ``cloudsql.googleapis.com``.
        ``allServices`` is a special value that covers all services. Required

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> name = client.secret_version_path('[PROJECT]', '[SECRET]', '[SECRET_VERSION]')
            >>>
            >>> response = client.access_secret_version(name)

        Args:
            name (str): A token to retrieve the next page of results. Pass this value in
                ``ListSecretVersionsRequest.page_token`` to retrieve the next page.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.secretmanager_v1.types.AccessSecretVersionResponse` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "access_secret_version" not in self._inner_api_calls:
            self._inner_api_calls[
                "access_secret_version"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.access_secret_version,
                default_retry=self._method_configs["AccessSecretVersion"].retry,
                default_timeout=self._method_configs["AccessSecretVersion"].timeout,
                client_info=self._client_info,
            )

        request = service_pb2.AccessSecretVersionRequest(name=name)
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("name", name)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        return self._inner_api_calls["access_secret_version"](
            request, retry=retry, timeout=timeout, metadata=metadata
        )

    def disable_secret_version(
        self,
        name,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
        Request message for ``SecretManagerService.ListSecretVersions``.

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> name = client.secret_version_path('[PROJECT]', '[SECRET]', '[SECRET_VERSION]')
            >>>
            >>> response = client.disable_secret_version(name)

        Args:
            name (str): The jstype option determines the JavaScript type used for values of
                the field. The option is permitted only for 64 bit integral and fixed
                types (int64, uint64, sint64, fixed64, sfixed64). A field with jstype
                JS_STRING is represented as JavaScript string, which avoids loss of
                precision that can happen when a large value is converted to a floating
                point JavaScript. Specifying JS_NUMBER for the jstype causes the
                generated JavaScript code to use the JavaScript "number" type. The
                behavior of the default option JS_NORMAL is implementation dependent.

                This option is an enum to permit additional types to be added, e.g.
                goog.math.Integer.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.secretmanager_v1.types.SecretVersion` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "disable_secret_version" not in self._inner_api_calls:
            self._inner_api_calls[
                "disable_secret_version"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.disable_secret_version,
                default_retry=self._method_configs["DisableSecretVersion"].retry,
                default_timeout=self._method_configs["DisableSecretVersion"].timeout,
                client_info=self._client_info,
            )

        request = service_pb2.DisableSecretVersionRequest(name=name)
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("name", name)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        return self._inner_api_calls["disable_secret_version"](
            request, retry=retry, timeout=timeout, metadata=metadata
        )

    def enable_secret_version(
        self,
        name,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
        Output only. The resource name of the ``SecretVersion`` in the
        format ``projects/*/secrets/*/versions/*``.

        ``SecretVersion`` IDs in a ``Secret`` start at 1 and are incremented for
        each subsequent version of the secret.

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> name = client.secret_version_path('[PROJECT]', '[SECRET]', '[SECRET_VERSION]')
            >>>
            >>> response = client.enable_secret_version(name)

        Args:
            name (str): A list of HTTP configuration rules that apply to individual API
                methods.

                **NOTE:** All service configuration rules follow "last one wins" order.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.secretmanager_v1.types.SecretVersion` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "enable_secret_version" not in self._inner_api_calls:
            self._inner_api_calls[
                "enable_secret_version"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.enable_secret_version,
                default_retry=self._method_configs["EnableSecretVersion"].retry,
                default_timeout=self._method_configs["EnableSecretVersion"].timeout,
                client_info=self._client_info,
            )

        request = service_pb2.EnableSecretVersionRequest(name=name)
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("name", name)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        return self._inner_api_calls["enable_secret_version"](
            request, retry=retry, timeout=timeout, metadata=metadata
        )

    def destroy_secret_version(
        self,
        name,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
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

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> name = client.secret_version_path('[PROJECT]', '[SECRET]', '[SECRET_VERSION]')
            >>>
            >>> response = client.destroy_secret_version(name)

        Args:
            name (str): Required. The list of Replicas for this ``Secret``.

                Cannot be empty.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.secretmanager_v1.types.SecretVersion` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "destroy_secret_version" not in self._inner_api_calls:
            self._inner_api_calls[
                "destroy_secret_version"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.destroy_secret_version,
                default_retry=self._method_configs["DestroySecretVersion"].retry,
                default_timeout=self._method_configs["DestroySecretVersion"].timeout,
                client_info=self._client_info,
            )

        request = service_pb2.DestroySecretVersionRequest(name=name)
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("name", name)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        return self._inner_api_calls["destroy_secret_version"](
            request, retry=retry, timeout=timeout, metadata=metadata
        )

    def set_iam_policy(
        self,
        resource,
        policy,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
        Required. The resource name of the ``Secret`` associated with the
        ``SecretVersions`` to list, in the format ``projects/*/secrets/*``.

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> # TODO: Initialize `resource`:
            >>> resource = ''
            >>>
            >>> # TODO: Initialize `policy`:
            >>> policy = {}
            >>>
            >>> response = client.set_iam_policy(resource, policy)

        Args:
            resource (str): REQUIRED: The resource for which the policy is being specified.
                See the operation documentation for the appropriate value for this field.
            policy (Union[dict, ~google.cloud.secretmanager_v1.types.Policy]): # gRPC Transcoding

                gRPC Transcoding is a feature for mapping between a gRPC method and one
                or more HTTP REST endpoints. It allows developers to build a single API
                service that supports both gRPC APIs and REST APIs. Many systems,
                including `Google APIs <https://github.com/googleapis/googleapis>`__,
                `Cloud Endpoints <https://cloud.google.com/endpoints>`__, `gRPC
                Gateway <https://github.com/grpc-ecosystem/grpc-gateway>`__, and
                `Envoy <https://github.com/envoyproxy/envoy>`__ proxy support this
                feature and use it for large scale production services.

                ``HttpRule`` defines the schema of the gRPC/REST mapping. The mapping
                specifies how different portions of the gRPC request message are mapped
                to the URL path, URL query parameters, and HTTP request body. It also
                controls how the gRPC response message is mapped to the HTTP response
                body. ``HttpRule`` is typically specified as an ``google.api.http``
                annotation on the gRPC method.

                Each mapping specifies a URL path template and an HTTP method. The path
                template may refer to one or more fields in the gRPC request message, as
                long as each field is a non-repeated field with a primitive
                (non-message) type. The path template controls how fields of the request
                message are mapped to the URL path.

                Example:

                ::

                    service Messaging {
                      rpc GetMessage(GetMessageRequest) returns (Message) {
                        option (google.api.http) = {
                            get: "/v1/{name=messages/*}"
                        };
                      }
                    }
                    message GetMessageRequest {
                      string name = 1; // Mapped to URL path.
                    }
                    message Message {
                      string text = 1; // The resource content.
                    }

                This enables an HTTP REST to gRPC mapping as below:

                HTTP \| gRPC -----|----- ``GET /v1/messages/123456`` \|
                ``GetMessage(name: "messages/123456")``

                Any fields in the request message which are not bound by the path
                template automatically become HTTP query parameters if there is no HTTP
                request body. For example:

                ::

                    service Messaging {
                      rpc GetMessage(GetMessageRequest) returns (Message) {
                        option (google.api.http) = {
                            get:"/v1/messages/{message_id}"
                        };
                      }
                    }
                    message GetMessageRequest {
                      message SubMessage {
                        string subfield = 1;
                      }
                      string message_id = 1; // Mapped to URL path.
                      int64 revision = 2;    // Mapped to URL query parameter `revision`.
                      SubMessage sub = 3;    // Mapped to URL query parameter `sub.subfield`.
                    }

                This enables a HTTP JSON to RPC mapping as below:

                HTTP \| gRPC -----|-----
                ``GET /v1/messages/123456?revision=2&sub.subfield=foo`` \|
                ``GetMessage(message_id: "123456" revision: 2 sub: SubMessage(subfield: "foo"))``

                Note that fields which are mapped to URL query parameters must have a
                primitive type or a repeated primitive type or a non-repeated message
                type. In the case of a repeated type, the parameter can be repeated in
                the URL as ``...?param=A&param=B``. In the case of a message type, each
                field of the message is mapped to a separate parameter, such as
                ``...?foo.a=A&foo.b=B&foo.c=C``.

                For HTTP methods that allow a request body, the ``body`` field specifies
                the mapping. Consider a REST update method on the message resource
                collection:

                ::

                    service Messaging {
                      rpc UpdateMessage(UpdateMessageRequest) returns (Message) {
                        option (google.api.http) = {
                          patch: "/v1/messages/{message_id}"
                          body: "message"
                        };
                      }
                    }
                    message UpdateMessageRequest {
                      string message_id = 1; // mapped to the URL
                      Message message = 2;   // mapped to the body
                    }

                The following HTTP JSON to RPC mapping is enabled, where the
                representation of the JSON in the request body is determined by protos
                JSON encoding:

                HTTP \| gRPC -----|----- ``PATCH /v1/messages/123456 { "text": "Hi!" }``
                \| ``UpdateMessage(message_id: "123456" message { text: "Hi!" })``

                The special name ``*`` can be used in the body mapping to define that
                every field not bound by the path template should be mapped to the
                request body. This enables the following alternative definition of the
                update method:

                ::

                    service Messaging {
                      rpc UpdateMessage(Message) returns (Message) {
                        option (google.api.http) = {
                          patch: "/v1/messages/{message_id}"
                          body: "*"
                        };
                      }
                    }
                    message Message {
                      string message_id = 1;
                      string text = 2;
                    }

                The following HTTP JSON to RPC mapping is enabled:

                HTTP \| gRPC -----|----- ``PATCH /v1/messages/123456 { "text": "Hi!" }``
                \| ``UpdateMessage(message_id: "123456" text: "Hi!")``

                Note that when using ``*`` in the body mapping, it is not possible to
                have HTTP parameters, as all fields not bound by the path end in the
                body. This makes this option more rarely used in practice when defining
                REST APIs. The common usage of ``*`` is in custom methods which don't
                use the URL at all for transferring data.

                It is possible to define multiple HTTP methods for one RPC by using the
                ``additional_bindings`` option. Example:

                ::

                    service Messaging {
                      rpc GetMessage(GetMessageRequest) returns (Message) {
                        option (google.api.http) = {
                          get: "/v1/messages/{message_id}"
                          additional_bindings {
                            get: "/v1/users/{user_id}/messages/{message_id}"
                          }
                        };
                      }
                    }
                    message GetMessageRequest {
                      string message_id = 1;
                      string user_id = 2;
                    }

                This enables the following two alternative HTTP JSON to RPC mappings:

                HTTP \| gRPC -----|----- ``GET /v1/messages/123456`` \|
                ``GetMessage(message_id: "123456")``
                ``GET /v1/users/me/messages/123456`` \|
                ``GetMessage(user_id: "me" message_id: "123456")``

                ## Rules for HTTP mapping

                1. Leaf request fields (recursive expansion nested messages in the
                   request message) are classified into three categories:

                   -  Fields referred by the path template. They are passed via the URL
                      path.
                   -  Fields referred by the ``HttpRule.body``. They are passed via the
                      HTTP request body.
                   -  All other fields are passed via the URL query parameters, and the
                      parameter name is the field path in the request message. A
                      repeated field can be represented as multiple query parameters
                      under the same name.

                2. If ``HttpRule.body`` is "*", there is no URL query parameter, all
                   fields are passed via URL path and HTTP request body.
                3. If ``HttpRule.body`` is omitted, there is no HTTP request body, all
                   fields are passed via URL path and URL query parameters.

                Path template syntax
                ~~~~~~~~~~~~~~~~~~~~

                ::

                    Template = "/" Segments [ Verb ] ;
                    Segments = Segment { "/" Segment } ;
                    Segment  = "*" | "**" | LITERAL | Variable ;
                    Variable = "{" FieldPath [ "=" Segments ] "}" ;
                    FieldPath = IDENT { "." IDENT } ;
                    Verb     = ":" LITERAL ;

                The syntax ``*`` matches a single URL path segment. The syntax ``**``
                matches zero or more URL path segments, which must be the last part of
                the URL path except the ``Verb``.

                The syntax ``Variable`` matches part of the URL path as specified by its
                template. A variable template must not contain other variables. If a
                variable matches a single path segment, its template may be omitted,
                e.g. ``{var}`` is equivalent to ``{var=*}``.

                The syntax ``LITERAL`` matches literal text in the URL path. If the
                ``LITERAL`` contains any reserved character, such characters should be
                percent-encoded before the matching.

                If a variable contains exactly one path segment, such as ``"{var}"`` or
                ``"{var=*}"``, when such a variable is expanded into a URL path on the
                client side, all characters except ``[-_.~0-9a-zA-Z]`` are
                percent-encoded. The server side does the reverse decoding. Such
                variables show up in the `Discovery
                Document <https://developers.google.com/discovery/v1/reference/apis>`__
                as ``{var}``.

                If a variable contains multiple path segments, such as ``"{var=foo/*}"``
                or ``"{var=**}"``, when such a variable is expanded into a URL path on
                the client side, all characters except ``[-_.~/0-9a-zA-Z]`` are
                percent-encoded. The server side does the reverse decoding, except "%2F"
                and "%2f" are left unchanged. Such variables show up in the `Discovery
                Document <https://developers.google.com/discovery/v1/reference/apis>`__
                as ``{+var}``.

                ## Using gRPC API Service Configuration

                gRPC API Service Configuration (service config) is a configuration
                language for configuring a gRPC service to become a user-facing product.
                The service config is simply the YAML representation of the
                ``google.api.Service`` proto message.

                As an alternative to annotating your proto file, you can configure gRPC
                transcoding in your service config YAML files. You do this by specifying
                a ``HttpRule`` that maps the gRPC method to a REST endpoint, achieving
                the same effect as the proto annotation. This can be particularly useful
                if you have a proto that is reused in multiple services. Note that any
                transcoding specified in the service config will override any matching
                transcoding configuration in the proto.

                Example:

                ::

                    http:
                      rules:
                        # Selects a gRPC method and applies HttpRule to it.
                        - selector: example.v1.Messaging.GetMessage
                          get: /v1/messages/{message_id}/{sub.subfield}

                ## Special notes

                When gRPC Transcoding is used to map a gRPC to JSON REST endpoints, the
                proto to JSON conversion must follow the `proto3
                specification <https://developers.google.com/protocol-buffers/docs/proto3#json>`__.

                While the single segment variable follows the semantics of `RFC
                6570 <https://tools.ietf.org/html/rfc6570>`__ Section 3.2.2 Simple
                String Expansion, the multi segment variable **does not** follow RFC
                6570 Section 3.2.3 Reserved Expansion. The reason is that the Reserved
                Expansion does not expand special characters like ``?`` and ``#``, which
                would lead to invalid URLs. As the result, gRPC Transcoding uses a
                custom encoding for multi segment variables.

                The path variables **must not** refer to any repeated or mapped field,
                because client libraries are not capable of handling such variable
                expansion.

                The path variables **must not** capture the leading "/" character. The
                reason is that the most common use case "{var}" does not capture the
                leading "/" character. For consistency, all path variables must share
                the same behavior.

                Repeated message fields must not be mapped to URL query parameters,
                because no client library can support such complicated mapping.

                If an API needs to use a JSON array for request or response body, it can
                map the request or response body to a repeated field. However, some gRPC
                Transcoding implementations may not support this feature.

                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.secretmanager_v1.types.Policy`
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.secretmanager_v1.types.Policy` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "set_iam_policy" not in self._inner_api_calls:
            self._inner_api_calls[
                "set_iam_policy"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.set_iam_policy,
                default_retry=self._method_configs["SetIamPolicy"].retry,
                default_timeout=self._method_configs["SetIamPolicy"].timeout,
                client_info=self._client_info,
            )

        request = iam_policy_pb2.SetIamPolicyRequest(resource=resource, policy=policy)
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("resource", resource)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        return self._inner_api_calls["set_iam_policy"](
            request, retry=retry, timeout=timeout, metadata=metadata
        )

    def get_iam_policy(
        self,
        resource,
        options_=None,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
        Gets the access control policy for a secret.
        Returns empty policy if the secret exists and does not have a policy set.

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> # TODO: Initialize `resource`:
            >>> resource = ''
            >>>
            >>> response = client.get_iam_policy(resource)

        Args:
            resource (str): REQUIRED: The resource for which the policy is being requested.
                See the operation documentation for the appropriate value for this field.
            options_ (Union[dict, ~google.cloud.secretmanager_v1.types.GetPolicyOptions]): javanano_as_lite

                If a dict is provided, it must be of the same form as the protobuf
                message :class:`~google.cloud.secretmanager_v1.types.GetPolicyOptions`
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.secretmanager_v1.types.Policy` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "get_iam_policy" not in self._inner_api_calls:
            self._inner_api_calls[
                "get_iam_policy"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.get_iam_policy,
                default_retry=self._method_configs["GetIamPolicy"].retry,
                default_timeout=self._method_configs["GetIamPolicy"].timeout,
                client_info=self._client_info,
            )

        request = iam_policy_pb2.GetIamPolicyRequest(
            resource=resource, options=options_
        )
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("resource", resource)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        return self._inner_api_calls["get_iam_policy"](
            request, retry=retry, timeout=timeout, metadata=metadata
        )

    def test_iam_permissions(
        self,
        resource,
        permissions,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None,
    ):
        """
        An annotation that describes a resource definition, see
        ``ResourceDescriptor``.

        Example:
            >>> from google.cloud import secretmanager_v1
            >>>
            >>> client = secretmanager_v1.SecretManagerServiceClient()
            >>>
            >>> # TODO: Initialize `resource`:
            >>> resource = ''
            >>>
            >>> # TODO: Initialize `permissions`:
            >>> permissions = []
            >>>
            >>> response = client.test_iam_permissions(resource, permissions)

        Args:
            resource (str): REQUIRED: The resource for which the policy detail is being requested.
                See the operation documentation for the appropriate value for this field.
            permissions (list[str]): Selects a method to which this rule applies.

                Refer to ``selector`` for syntax details.
            retry (Optional[google.api_core.retry.Retry]):  A retry object used
                to retry requests. If ``None`` is specified, requests will
                be retried using a default configuration.
            timeout (Optional[float]): The amount of time, in seconds, to wait
                for the request to complete. Note that if ``retry`` is
                specified, the timeout applies to each individual attempt.
            metadata (Optional[Sequence[Tuple[str, str]]]): Additional metadata
                that is provided to the method.

        Returns:
            A :class:`~google.cloud.secretmanager_v1.types.TestIamPermissionsResponse` instance.

        Raises:
            google.api_core.exceptions.GoogleAPICallError: If the request
                    failed for any reason.
            google.api_core.exceptions.RetryError: If the request failed due
                    to a retryable error and retry attempts failed.
            ValueError: If the parameters are invalid.
        """
        # Wrap the transport method to add retry and timeout logic.
        if "test_iam_permissions" not in self._inner_api_calls:
            self._inner_api_calls[
                "test_iam_permissions"
            ] = google.api_core.gapic_v1.method.wrap_method(
                self.transport.test_iam_permissions,
                default_retry=self._method_configs["TestIamPermissions"].retry,
                default_timeout=self._method_configs["TestIamPermissions"].timeout,
                client_info=self._client_info,
            )

        request = iam_policy_pb2.TestIamPermissionsRequest(
            resource=resource, permissions=permissions
        )
        if metadata is None:
            metadata = []
        metadata = list(metadata)
        try:
            routing_header = [("resource", resource)]
        except AttributeError:
            pass
        else:
            routing_metadata = google.api_core.gapic_v1.routing_header.to_grpc_metadata(
                routing_header
            )
            metadata.append(routing_metadata)

        return self._inner_api_calls["test_iam_permissions"](
            request, retry=retry, timeout=timeout, metadata=metadata
        )
