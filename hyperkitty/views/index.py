#-*- coding: utf-8 -*-
# Copyright (C) 2014-2015 by the Free Software Foundation, Inc.
#
# This file is part of HyperKitty.
#
# HyperKitty is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# HyperKitty is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# HyperKitty.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Aurelien Bompard <abompard@fedoraproject.org>
#

from __future__ import absolute_import, unicode_literals

import datetime

from django.shortcuts import render
from django.conf import settings

from hyperkitty.lib.view_helpers import show_mlist, is_mlist_authorized
from hyperkitty.models import MailingList


def index(request):
    now = datetime.datetime.now()
    lists = [
        ml for ml in MailingList.objects.all()
        if not settings.FILTER_VHOST or show_mlist(ml, request) ]
    initials = set()
    for mlist in lists:
        if not mlist.is_private:
            mlist.can_view = True
        else:
            if is_mlist_authorized(request, mlist):
                mlist.can_view = True
            else:
                mlist.can_view = False
        if mlist.can_view:
            mlist.recent_threads_count = mlist.recent_threads.count()
        else:
            mlist.recent_threads_count = None
        initials.add(mlist.name[0])

    # sorting
    sort_mode = request.GET.get('sort')
    if not sort_mode:
        sort_mode = "popular"
    if sort_mode == "name":
        pass # already sorted by name
    elif sort_mode == "active":
        # Don't show private lists when sorted by activity, to avoid disclosing
        # info about the private list's activity
        lists = [ l for l in lists if l.is_private == False ]
        lists.sort(key=lambda l: l.recent_threads_count, reverse=True)
    elif sort_mode == "popular":
        # Don't show private lists when sorted by popularity, to avoid disclosing
        # info about the private list's popularity
        lists = [ l for l in lists if l.is_private == False ]
        lists.sort(key=lambda l: l.recent_participants_count, reverse=True)
    elif sort_mode == "creation":
        lists.sort(key=lambda l: l.created_at, reverse=True)
    else:
        return HttpResponse("Wrong search parameter",
                            content_type="text/plain", status=500)

    context = {
        'view_name': 'all_lists',
        'all_lists': lists,
        'initials': sorted(list(initials)),
        'sort_mode': sort_mode,
        }
    return render(request, "hyperkitty/index.html", context)
