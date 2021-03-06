# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the read view file for the iris-submissions application.

Views for listing single and multiple item info is contained here.
"""
# pylint: disable=E1101,C0111,W0622,C0301

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator


from iris.core.models import Submission, BuildGroup, SubmissionGroup


def index(request):
    """
    Index page of Submissions app.
    If a user logged-in, redirect to "my submissions" page,
    otherwise redirect to "opened submissions" page.
    """
    if request.user.is_authenticated():
        url = reverse('my_submissions')
    else:
        url = reverse('opened_submissions')
    return HttpResponseRedirect(url)


def opened(request):
    """
    All opened submissions
    """
    res = Submission.objects.exclude(
        status='33_ACCEPTED').exclude(
        status='36_REJECTED')
    return render(request, 'submissions/summary.html', {
            'title': 'All open submissions',
            'results': SubmissionGroup.group(res),
            })

def accepted(request):
    """
    All accepted submissions
    """
    res = Submission.objects.filter(status='33_ACCEPTED')
    return render(request, 'submissions/summary.html', {
            'title': 'All accepted submissions',
            'results': SubmissionGroup.group(res),
            })


def rejected(request):
    """
    All rejected submissions
    """
    res = Submission.objects.filter(status='36_REJECTED')
    return render(request, 'submissions/summary.html', {
            'title': 'All rejected submissions',
            'results': SubmissionGroup.group(res),
            })


@login_required
def mine(request):
    """
    All my (the logged-in user) opened submissions
    """
    res = Submission.objects.filter(owner=request.user)
    return render(request, 'submissions/summary.html', {
            'title': 'My submissions',
            'results': SubmissionGroup.group(
                Submission.objects.filter(owner=request.user)),
            })


def search(request):
    """
    Search submissions by keyword
    """
    kw = request.GET.get('kw')
    subs = Submission.objects.filter(
        Q(name__contains=kw) |
        Q(commit__startswith=kw) |
        Q(owner__email__startswith=kw) |
        Q(gittree__gitpath__contains=kw)
        )
    return render(request, 'submissions/summary.html', {
            'title': 'Search result for "%s"' % kw,
            'results': SubmissionGroup.group(subs),
            })


def detail(request, tag):
    """
    Detail info about a submission group identified by certain tag
    """
    groups = SubmissionGroup.group(
        Submission.objects.filter(name=tag.rstrip('/')))
    if not groups:
        raise Http404

    assert len(groups) == 1  # because it's group by tag
    sgroup = groups[0]
    bgroups = submission_group_to_build_groups(sgroup)

    return render(request, 'submissions/detail.html', {
            'sgroup': sgroup,
            'bgroups': bgroups,
            })


def submission_group_to_build_groups(sgroup):
    """
    Find build groups by submission group (tag)
    """
    return {sbuild.group
            for submission in sgroup.subs
            for sbuild in submission.submissionbuild_set.all()}
