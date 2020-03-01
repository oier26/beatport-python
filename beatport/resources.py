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


class Resource:
    """
    Base class for any resource.
    It is mainly responsible of passing a reference to the client
    to this class when instantiated, and transmit the json data into
    attributes
    """

    def __init__(self, client, json):
        self._fields = tuple(json.keys())
        self.client = client
        for key in json:
            setattr(self, key, json[key])

    def __repr__(self):
        name = getattr(self, "name", getattr(self, "title", None))
        if name is not None:
            return "<{}: {}>".format(self.__class__.__name__, str(name))
        return super().__repr__()

    def as_dict(self):
        """
        Convert resource to dictionary
        """
        result = {}
        for key in self._fields:
            value = getattr(self, key)
            if isinstance(value, list):
                value = [i.as_dict() if isinstance(i, Resource) else i for i in value]
            if isinstance(value, Resource):
                value = value.as_dict()
            result[key] = value
        return result

    def iter_relation(self, relation, **kwargs):
        """
        Generic method to iterate relation from any resource.
        Query the client with the object's known parameters
        and try to retrieve the provided relation type. This
        is not meant to be used directly by a client, it's more
        a helper method for the child objects.
        """
        index = 0
        while 1:
            items = self.get_relation(relation, index=index, **kwargs)
            for item in items:
                yield item

            if len(items) == 0:
                break
            index += len(items)


class Artist(Resource):
    artists = None

    def get_artists(self):
        return self.artists


class Chart(Resource):
    charts = None

    def get_charts(self):
        return self.charts


class Genre(Resource):
    genres = None

    def get_genres(self):
        return self.genres


class Label(Resource):
    labels = None

    def get_labels(self):
        return self.labels


class MusicalKey(Resource):
    musical_keys = None

    def get_musical_keys(self):
        return self.musical_keys


class Release(Resource):
    releases = None

    def get_releases(self):
        return self.releases


class Track(Resource):
    tracks = None

    def get_tracks(self):
        return self.tracks
