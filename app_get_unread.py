#!/usr/bin/env python3

import sys

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_unread(creds):
    try:
        ids = set()
        threads = set()
        pageToken = None
        while True:
            service = build('gmail', 'v1', credentials=creds)
            msg_getter = service.users().messages()
            getter = msg_getter.list(userId='me',
                                     labelIds=['INBOX', 'UNREAD'],
                                     pageToken = pageToken)
            results = getter.execute()
            sys.stderr.write('batch ids %d threads %d' % (
                len(ids), len(threads)))
            sys.stderr.flush()
            #fname = 'msgs.json'
            #open(fname, 'w').write(json.dumps(results, indent=2))
            for msg in results['messages']:
                ids.add(msg['id'])
                threads.add(msg['threadId'])
                msg_msg = msg_getter.get(userId='me',
                                         id=msg['id'],
                                         format='metadata').execute()
                msg_hdrs = msg_msg['payload']['headers']
                for msg_hdr in msg_hdrs:
                    if msg_hdr['name'].lower() == 'from':
                        print(msg_hdr['value'])
                        break
                sys.stderr.write('\rbatch ids %d threads %d' % (
                    len(ids), len(threads)))
                sys.stderr.flush()

            sys.stderr.write('\n')
            sys.stderr.flush()

            pageToken = results.get('nextPageToken', None)
            if pageToken is None or not pageToken:
                break

        sys.stderr.write('messages : %d\n' % len(ids))
        sys.stderr.write('threads  : %d\n' % len(threads))

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    from auth_cloud import auth
    creds = auth(scopes)
    get_unread(creds)
