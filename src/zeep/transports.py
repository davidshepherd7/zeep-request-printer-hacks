import logging
import os
from contextlib import contextmanager
from urllib.parse import urlparse

import requests

from zeep.utils import get_media_type, get_version
from zeep.wsdl.utils import etree_to_string


class Transport:
    """The transport object handles all communication to the SOAP server.

    :param cache: The cache object to be used to cache GET requests
    :param timeout: The timeout for loading wsdl and xsd documents.
    :param operation_timeout: The timeout for operations (POST/GET). By
                              default this is None (no timeout).
    :param session: A :py:class:`request.Session()` object (optional)

    """

    def __init__(self, cache=None, timeout=300, operation_timeout=None, session=None):
        self.cache = cache
        self.load_timeout = timeout
        self.operation_timeout = operation_timeout
        self.logger = logging.getLogger(__name__)

        self.session = session or requests.Session()
        self.session.headers["User-Agent"] = "Zeep/%s (www.python-zeep.org)" % (
            get_version()
        )

    def get(self, address, params, headers):
        """Proxy to requests.get()

        :param address: The URL for the request
        :param params: The query parameters
        :param headers: a dictionary with the HTTP headers.

        """
        print(f"GET {address}, params: {params}, headers: {headers}")
        raise NotImplementedError("Not making request")

    def post(self, address, message, headers):
        """Proxy to requests.posts()

        :param address: The URL for the request
        :param message: The content for the body
        :param headers: a dictionary with the HTTP headers.

        """
        if self.logger.isEnabledFor(logging.DEBUG):
            log_message = message
            if isinstance(log_message, bytes):
                log_message = log_message.decode("utf-8")
            self.logger.debug("HTTP Post to %s:\n%s", address, log_message)

        print(f"POST {address}, data: {message}, headers: {headers}")
        raise NotImplementedError("Not making real request")

    def post_xml(self, address, envelope, headers):
        """Post the envelope xml element to the given address with the headers.

        This method is intended to be overriden if you want to customize the
        serialization of the xml element. By default the body is formatted
        and encoded as utf-8. See ``zeep.wsdl.utils.etree_to_string``.

        """
        message = etree_to_string(envelope)
        return self.post(address, message, headers)

    def load(self, url):
        """Load the content from the given URL"""
        if not url:
            raise ValueError("No url given to load")

        scheme = urlparse(url).scheme
        if scheme in ("http", "https"):

            if self.cache:
                response = self.cache.get(url)
                if response:
                    return bytes(response)

            content = self._load_remote_data(url)

            if self.cache:
                self.cache.add(url, content)

            return content

        elif scheme == "file":
            if url.startswith("file://"):
                url = url[7:]

        with open(os.path.expanduser(url), "rb") as fh:
            return fh.read()

    def _load_remote_data(self, url):
        self.logger.debug("Loading remote data from: %s", url)
        response = self.session.get(url, timeout=self.load_timeout)
        response.raise_for_status()
        return response.content

    @contextmanager
    def settings(self, timeout=None):
        """Context manager to temporarily overrule options.

        Example::

            transport = zeep.Transport()
            with transport.settings(timeout=10):
                client.service.fast_call()

        :param timeout: Set the timeout for POST/GET operations (not used for
                        loading external WSDL or XSD documents)

        """
        old_timeout = self.operation_timeout
        self.operation_timeout = timeout
        yield
        self.operation_timeout = old_timeout
