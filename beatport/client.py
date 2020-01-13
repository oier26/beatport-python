# -*- coding: utf-8 -*-
# This file is part of beatport-python.
# Copyright 2020, Oier Arroniz.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

import logging

from requests_oauthlib import OAuth1Session
from requests_oauthlib.oauth1_session import (TokenRequestDenied, TokenMissing,
                                              VerifierMissing)

import beatport

AUTH_ERRORS = (TokenRequestDenied, TokenMissing, VerifierMissing)


class Client:
    use_ssl = True
    host = "oauth-api.beatport.com"
    api_version = "3"
    access_token = None
    access_secret = None

    def __init__(self, api_key, api_secret, **kwargs):
        """ Initiate the client with OAuth information.
        For the initial authentication with the backend `auth_key` and
        `auth_secret` can be `None`. Use `get_authorize_url` and
        `get_access_token` to obtain them for subsequent uses of the API.
        :param api_key:     OAuth1 client key
        :param api_secret:  OAuth1 client secret
        """
        super().__init__()

        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = kwargs.get("access_token", None)
        self.access_secret = kwargs.get("access_secret", None)

        self.session = OAuth1Session(
            client_key=self.api_key, client_secret=self.api_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_secret,
            callback_uri='oob')
        self.session.headers = {'User-Agent': beatport.USER_AGENT}
        if kwargs.get("headers"):
            self.session.headers.update(kwargs.get("headers"))

        if kwargs.get("auth_response"):
            self.authenticate(kwargs.get("auth_response"))
        elif self.access_token is None and self.access_secret is None:
            print(f"Log in to your Beatport account in: {self.get_authorize_url()}")

    def get_authorize_url(self):
        """ Generate the URL for the user to authorize the application.
        Retrieves a request token from the Beatport API and returns the
        corresponding authorization URL on their end that the user has
        to visit.
        This is the first step of the initial authorization process with the
        API. Once the user has visited the URL, call
        :py:method:`get_access_token` with the displayed data to complete
        the process.
        :returns:   Authorization URL for the user to visit
        :rtype:     unicode
        """
        self.session.fetch_request_token(
            self.make_url('/identity/1/oauth/request-token'))
        return self.session.authorization_url(
            self.make_url('/identity/1/oauth/authorize'))

    def get_access_token(self, auth_response):
        """ Obtain the final access token and secret for the API.
        :param auth_response: URL-encoded authorization data as displayed at
                              the authorization url (obtained via
                              :py:meth:`get_authorize_url`) after signing in
        :type auth_data:      unicode
        :returns:             OAuth resource owner key and secret
        :rtype:               (unicode, unicode) tuple
        """
        self.session.parse_authorization_response(
            f"/identity/1/oauth/authorize?{auth_response}")
        access_data = self.session.fetch_access_token(
            self.make_url('/identity/1/oauth/access-token'))
        return access_data['oauth_token'], access_data['oauth_token_secret']

    def authenticate(self, auth_response):
        try:
            self.access_token, self.access_secret = self.get_access_token(auth_response)
        except AUTH_ERRORS as e:
            logging.error(f"Beatport token authentication request failed: {e}")
            raise e

    def make_url(self, request=""):
        """Build the url with the appended request if provided."""
        if request.startswith("/"):
            request = request[1:]
        return f"{self.protocol}://{self.host}/{request}"

    def get_query(self, endpoint, **kwargs):
        """ Perform a GET request on a given API endpoint.
        Automatically extracts result data from the response and converts HTTP
        exceptions into :py:class:`BeatportAPIError` objects.
        """
        try:
            response = self.session.get(self.make_url(endpoint), params=kwargs)
        except Exception as e:
            logging.error(f"Error connecting to Beatport API: {e}")
            raise e
        if not response:
            raise logging.error(
                f"Error {response.status_code} for '{response.request.path_url}")
        return response.json()['results']

    @property
    def protocol(self):
        """
        Get the http prefix for the address depending on the use_ssl attribute
        """
        return "https" if self.use_ssl else "http"
