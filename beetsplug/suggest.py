# This file is part of beets.
# Copyright 2015, Cody Reichert <codyreichert@gmail.com>.
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

"""Generates suggestions for new artist based off of beets queries.
"""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)

import pylast

from beets import plugins, ui
from beets.util import mkdirall, normpath, syspath
from beets.library import Item, Album, parse_query_string
from beets.dbcore import OrQuery, FieldQuery
from beets.dbcore.query import MultipleSort
import os


class SuggestPlugin(plugins.BeetsPlugin):

    def __init__(self):
        super(SuggestPlugin, self).__init__()

        self.config.add({
            'limit': u'5',
            'threshold': u'0.5',
        })
        self.client = pylast.LastFMNetwork(api_key=plugins.LASTFM_KEY)


    def commands(self):
        suggest_now = ui.Subcommand('suggest',
                                    help='lookup music suggestions for a beets query.'
                                         ' $ beets suggest [query]')

        suggest_now.func = self.get_suggestions
        return [suggest_now]


    def get_suggestions(self, lib, opts, args):
        if not args:
            self._log.info('You must supply a query so I can make suggestions')
            return

        queries = ui.decargs(args)
        lookups = self._lookup_list(lib, queries)

        self._log.info('Let\'s find artists similar to:\n{0}', (', '.join(lookups)))
        initial_matches = self.last_lookup_artist(lib, lookups)
        self._matches_threshold_filter(lib, initial_matches)


    def _lookup_list(self, lib, queries):
        lookups = set()
        for q in queries:
            results = lib.items(q)
            for r in results:
                lookups.add(r.albumartist)

        return lookups


    def last_lookup_artist(self, lib, artists):
        """Take a list of artists (which are arguments passed from the command line)
        and lookup top similar artists from Last.FM. It logs results to the console
        with the limit set from the beets config file.
        """
        ss = set()
        for artist in artists:
            artist = self._artist(artist)
            matches = self._get_similar(artist, self.config['limit'])
            for match in matches:
                if not match in artists:
                    m = str(match.item).decode('utf-8')
                    r = str(match.match)
                    ss.add((m, r))

        self._log.info('\n\nHere\'s some suggestions:\n')
        print(list(ss))
        return ss


    def _artist(self, artist):
        return self.client.get_artist(artist)


    def _get_similar(self, artist, limit):
        return artist.get_similar(limit)


    def _matches_threshold_filter(self, lib, matches):
        return
