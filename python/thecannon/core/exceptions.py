# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2017-12-05 12:01:21
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2017-12-05 12:19:32

from __future__ import print_function, division, absolute_import


class ThecannonError(Exception):
    """A custom core Thecannon exception"""

    def __init__(self, message=None):

        message = 'There has been an error' \
            if not message else message

        super(ThecannonError, self).__init__(message)


class ThecannonNotImplemented(ThecannonError):
    """A custom exception for not yet implemented features."""

    def __init__(self, message=None):

        message = 'This feature is not implemented yet.' \
            if not message else message

        super(ThecannonNotImplemented, self).__init__(message)


class ThecannonAPIError(ThecannonError):
    """A custom exception for API errors"""

    def __init__(self, message=None):
        if not message:
            message = 'Error with Http Response from Thecannon API'
        else:
            message = 'Http response error from Thecannon API. {0}'.format(message)

        super(ThecannonAPIError, self).__init__(message)


class ThecannonApiAuthError(ThecannonAPIError):
    """A custom exception for API authentication errors"""
    pass


class ThecannonMissingDependency(ThecannonError):
    """A custom exception for missing dependencies."""
    pass


class ThecannonWarning(Warning):
    """Base warning for Thecannon."""


class ThecannonUserWarning(UserWarning, ThecannonWarning):
    """The primary warning class."""
    pass


class ThecannonSkippedTestWarning(ThecannonUserWarning):
    """A warning for when a test is skipped."""
    pass


class ThecannonDeprecationWarning(ThecannonUserWarning):
    """A warning for deprecated features."""
    pass
