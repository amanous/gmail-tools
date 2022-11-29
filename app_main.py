#!/usr/bin/env python3

from argparse import ArgumentParser

from googleapiclient.discovery import build

def main(get_creds, service_kwargs, commands):
    parser = ArgumentParser(prog = 'gmailtool')
    parser.add_argument('command', choices = commands.keys())

    args = parser.parse_args()

    scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = get_creds(scopes)
    service = build('gmail', 'v1', credentials=creds, **service_kwargs)

    commands[args.command](service)

if __name__ == '__main__':
    from auth_cloud import get_creds
    service_kwargs = {}
    from app_get_unread import get_unread
    from app_get_filters import get_filters
    commands = {
        'unread': get_unread,
        'filters': get_filters,
    }
    main(get_creds, service_kwargs, commands)
