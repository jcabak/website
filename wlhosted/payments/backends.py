# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2018 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <https://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from __future__ import unicode_literals

from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from wlhosted.payments.models import Payment

BACKENDS = {}


def get_backend(name):
    backend = BACKENDS[name]
    if backend.debug and not settings.PAYMENT_DEBUG:
        raise KeyError('Invalid backend')
    return backend


def list_backends():
    for backend in BACKENDS.values():
        if not backend.debug or settings.PAYMENT_DEBUG:
            yield backend


class InvalidState(ValueError):
    pass


def register_backend(backend):
    BACKENDS[backend.name] = backend
    return backend


class Backend(object):
    name = None
    debug = False
    verbose = None

    def __init__(self, payment):
        select = Payment.objects.filter(pk=payment.pk).select_for_update()
        self.payment = select[0]

    def perform(self, request):
        """Performs payment and optionally redirects user."""
        raise NotImplementedError()

    def collect(self, request):
        """Collects payment information."""
        raise NotImplementedError()

    def initiate(self, request):
        """Initiates payment and optionally redirects user."""
        if self.payment.state != Payment.NEW:
            raise InvalidState()

        result = self.perform(request)

        # Update payment state
        self.payment.state = Payment.PENDING
        self.payment.details['backend'] = self.name
        self.payment.save()

        return result

    def complete(self, request):
        """Payment completion called from returned request."""
        if self.payment.state != Payment.PENDING:
            raise InvalidState()

        if self.collect(request):
            self.success()
            return True
        self.failure()
        return False

    def generate_invoice(self):
        """Generates an invoice."""
        self.payment.invoice = 'XXX'
        self.payment.save()

    def notify_user(self):
        """Send email notification with an invoice."""

    def success(self):
        self.payment.state = Payment.ACCEPTED
        self.payment.save()

        self.generate_invoice()
        self.notify_user()

    def failure(self):
        self.payment.state = Payment.REJECTED
        self.payment.save()


@register_backend
class DebugPay(Backend):
    name = 'pay'
    debug = True
    verbose = 'Pay'

    def perform(self, request):
        return None

    def collect(self, request):
        return True


@register_backend
class DebugReject(DebugPay):
    name = 'reject'
    verbose = 'Reject'

    def collect(self, request):
        self.payment.extra['reject_reason'] = 'Debug reject'
        return False


@register_backend
class DebugPending(DebugPay):
    name = 'pending'
    verbose = 'Pending'

    def perform(self, request):
        return redirect('https://cihar.com/')

    def collect(self, request):
        return True
