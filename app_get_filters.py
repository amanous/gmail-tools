#!/usr/bin/env python3

import json

from googleapiclient.errors import HttpError


class Op(object):
    class __op(object):
        def __init__(self, s):
            self.s = s
        def __str__(self):
            return self.s
    TOP = __op('TOP')
    OR  = __op('OR')
    AND = __op('AND')
    GRP = __op('GRP')

class Node(object):
    def __init__(self, up, op, data):
        self.up = up
        self.down = []
        self.op = op
        self.data = data

    def add(self, op, data = None):
        n = Node(self, op, data)
        self.down.append(n)
        return n

    def print(self, suffix = ''):
        s = suffix
        if self.op:
            s += str(self.op) + ' '
        if self.data:
            s += self.data
        print(s)
        for c in self.down:
            c.print(suffix + '    ')

class CantParse(Exception):
    def __init__(self, data, i):
        self.data = data
        self.i = i

def parse(search):
    top = Node(None, Op.TOP, None)
    append = top
    up = top
    data = ''
    for i in range(len(search)):
        c = search[i]
        #print(c, top.op)
        if c == '(':
            if data:
                append = append.add(None, data)
                data = ''
            append = append.add(Op.GRP)
            up = append
        elif c == ')':
            if append.op not in (Op.AND, Op.OR):
                raise CantParse(search, i)
            if data:
                append.add(None, data)
                data = ''
            up = up.up
            append = up
        elif c == '{':
            if data:
                append = append.add(None, data)
                data = ''
            append = append.add(Op.OR)
            up = append
        elif c == '}':
            if append.op != Op.OR:
                raise CantParse(search, i)
            if data:
                append.add(None, data)
                data = ''
            up = up.up
            append = up
        elif c == ' ':
            if data == 'OR':
                if append.op == Op.GRP:
                    append.op = Op.OR
                if append.op not in (Op.GRP, Op.TOP, Op.OR):
                    raise CantParse(search, i)
            elif data:
                append.add(None, data)
            data = ''
        else:
            data += c
    if data:
        append.add(None, data)
    return top

def printFilter(fl, label_map):
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
            print('    ', '--')
            parse(flcr).print(suffix = '     ')
        else:
            print('  ', 'KEY', 'BOOL', k, '=', flcr)

    for k, v in fl['action'].items():
        if k in ('addLabelIds', 'removeLabelIds'):
            print(k, list(map(lambda v:label_map[v], v)))
        else:
            print(k, v)

def get_filters(service):
    try:
        getter = service.users().labels().list(userId='me')
        results = getter.execute()
        labels = {}
        for label in results.get('labels', []):
            labels[label['id']] = label['name']

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
            printFilter(fl, labels)
        for fl in filters_actions:
            printFilter(fl, labels)

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
