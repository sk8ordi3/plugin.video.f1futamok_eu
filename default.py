# -*- coding: utf-8 -*-

'''
    F1futamok.eu Add-on
    Copyright (C) 2020 heg, vargalex

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import sys
from resources.lib.indexers import navigator

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl

params = dict(parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')
url = params.get('url')

image_url = params.get('image_url')
title = params.get('title')

if action is None:
    navigator.navigator().root()

elif action == 'categories':
    navigator.navigator().getCategorys(url)

elif action == 'ext_categs':
    navigator.navigator().extCatergorys(url, image_url, title)

elif action == 'ext_video':
    navigator.navigator().extVideo(url, image_url, title)

elif action == 'play_movie':
    navigator.navigator().playMovie(url)

elif action == 'newsearch':
    navigator.navigator().doSearch(url)