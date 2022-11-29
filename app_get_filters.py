#!/usr/bin/env python3

import json

from googleapiclient.errors import HttpError


def printFilter(fl):
    print()
    #print(fl['id'])
    print('criteria:')
    for k in sorted(fl['criteria']):
        flcr = fl['criteria'][k]
        if type(flcr) != type(True):
            if ' ' not in flcr:
                print('  ', 'KEY', 'SIMPLE', k, ':', flcr)
                continue
            print('  ', 'KEY', 'COMPLEX', k, ':')
            print('    ', flcr)
            #print('    ', '--')
            #parse(flcr).print(suffix = '     ')
        else:
            print('  ', 'KEY', 'BOOL', k, '=', flcr)

    for k, v in fl['action'].items():
        print (k, v)


def get_filters(service):
    try:
        getter = service.users().settings().filters().list(userId='me')
        results = getter.execute()
        filters = results.get('filter', [])

        filters_add_label = []
        filters_actions = []
        while filters:
            fl = filters.pop(0)
            if set(fl['action'].keys()) == set(['addLabelIds']):
                filters_add_label.append(fl)
            else:
                filters_actions.append(fl)

        for fl in filters_add_label:
            printFilter(fl)
        for fl in filters_actions:
            printFilter(fl)

        if False:
            fname = 'filters.json'
            open(fname, 'w').write(json.dumps(filters, indent=2))
            print('wrote', fname)
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    from auth_cloud import get_creds
    creds = get_creds(scopes)
    from googleapiclient.discovery import build
    service = build('gmail', 'v1', credentials=creds)
    get_filters(service)
