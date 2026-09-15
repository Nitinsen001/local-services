"""Temporary all-pages verification harness (deleted after the UI refactor).

Renders every route as anonymous / customer / provider and reports:
  - HTTP status (a 500 or template error is reported with its exception)
  - HTML well-formedness (unclosed or stray tags)
  - whether the shared theme header/footer are present
"""
import os
import traceback
from html.parser import HTMLParser

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cityservices.settings')
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from django.test import Client  # noqa: E402
from django.urls import reverse  # noqa: E402

from services.models import Service  # noqa: E402

VOID = {'meta', 'link', 'br', 'img', 'input', 'hr', 'source', 'area', 'base',
        'col', 'embed', 'param', 'track', 'wbr'}


class Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f'stray </{tag}> at {self.getpos()}')
            return
        open_tag, pos = self.stack.pop()
        if open_tag != tag:
            self.errors.append(f'</{tag}> at {self.getpos()} closes <{open_tag}> from {pos}')


service = Service.objects.filter(available=True).first()
provider_user = User.objects.filter(profile__is_provider=True, service__isnull=False).distinct().first()

ROUTES = [
    ('home', {}),
    ('about', {}),
    ('contact', {}),
    ('accounts:register', {}),
    ('accounts:login', {}),
    ('accounts:profile', {}),
    ('accounts:account_settings', {}),
    ('accounts:privacy_security', {}),
    ('accounts:provider_dashboard', {}),
    ('accounts:user_dashboard', {}),
    ('accounts:notifications', {}),
    ('services:service_list', {}),
    ('services:service_detail', {'pk': service.id} if service else None),
    ('services:add_service', {}),
    ('services:favorite_list', {}),
    ('services:availability', {}),
    ('bookings:my_bookings', {}),
    ('bookings:billing_history', {}),
    ('bookings:provider_bookings', {}),
    ('bookings:book_service', {'service_id': service.id} if service else None),
    ('reviews:add_review', {'service_id': service.id} if service else None),
    ('reviews:provider_reviews', {'provider_id': provider_user.id} if provider_user else None),
    ('chat:chat_with_user', {'user_id': provider_user.id} if provider_user else None),
]

customer = User.objects.filter(profile__is_provider=False).first()
client = Client()

for actor, user in (('anon', None), ('customer', customer), ('provider', provider_user)):
    if actor != 'anon' and user is None:
        print(f'== {actor}: no user in database, skipped')
        continue
    print(f'== {actor} ({getattr(user, "username", "-")})')
    if user:
        client.force_login(user)
    else:
        client.logout()
    for name, kwargs in ROUTES:
        if kwargs is None:
            print(f'   SKIP  {name} (missing fixture data)')
            continue
        try:
            url = reverse(name, kwargs=kwargs)
        except Exception as exc:
            print(f'   FAIL  {name}: reverse() -> {exc}')
            continue
        try:
            response = client.get(url, HTTP_HOST='localhost', follow=False)
        except Exception:
            print(f'   ERROR {name} {url}')
            traceback.print_exc()
            continue
        body = response.content.decode() if response.status_code == 200 else ''
        detail = []
        if response.status_code == 200:
            checker = Checker()
            checker.feed(body)
            leftover = [t for t, _ in checker.stack]
            if leftover:
                detail.append(f'unclosed={leftover}')
            if checker.errors:
                detail.append(f'tagerrors={checker.errors[:2]}')
            if 'site-header' not in body or 'site-footer' not in body:
                detail.append('missing shared chrome')
        print(f'   {response.status_code}   {name} {url} {" ".join(detail)}')
    if user:
        client.logout()