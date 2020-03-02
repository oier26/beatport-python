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

"""
Python Beatport API <https://oauth-api.beatport.com> Wrapper.
"""
import pytest

import beatport


@pytest.mark.parametrize("api_key", ['57713c3906af6f5def151b33601389176b37b429'])
@pytest.mark.parametrize("api_secret", ['b3fe08c93c80aefd749fe871a16cd2bb32e2b954'])
@pytest.mark.parametrize("access_token", ['77beecc7fd51e69142d5d78312421f8ef421981b'])
@pytest.mark.parametrize("access_secret", ['7b6a2178d4315ea2bbf47597306f445296465839'])
@pytest.mark.parametrize("auth_response", ['oauth_token=ebef014e0fac2a767c4b579840e24da887273369&oauth_verifier=' +
                                           '01749676015e0349f0aaf1fcccf97b9c&oauth_callback_confirmed=true'])
@pytest.fixture
def fixture_client(api_key, api_secret, access_token, access_secret):
    client = beatport.Client(api_key=api_key, api_secret=api_secret,
                             access_token=access_token, access_secret=access_secret)
    return client


@pytest.mark.parametrize("url", ['/catalog/3/tracks'])
@pytest.mark.parametrize("track_id", ['12857425'])
def test_authorize(fixture_client, url, track_id):
    assert fixture_client.get_query(url, id=track_id) is not None
    print(fixture_client.get_query(url, id=track_id))
