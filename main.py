import json
import sys
import argparse
import os
import requests
import re
import hipchat
import time
__author__ = 'omeraplak'


def main(**kwargs):
    global arg
    arg = kwargs
    print(arg['username'])
    print(arg['password'])

    hipster = hipchat.HipChat(token=arg['hipchattoken'])
    params = {'duration': arg['duration'], 'subject[chart][id]': arg['chartid'], 'subject[chart][source]':'', 'subject[chart][type]':arg['charttype']}
    url = 'https://metrics.librato.com/metrics-api/v1/snapshots'
    snapshotRequest = requests.post(url, params=params, auth=(arg['username'], arg['password']))

    if snapshotRequest.status_code == 401:
        print("Not Authrozied Librato")
        sys.exit(2)

    snapshotRequestResponse = json.loads(snapshotRequest.text)
    print(snapshotRequestResponse['href'])

    readyImage = False
    while not readyImage:
        snapshotImageRequest = requests.get(snapshotRequestResponse['href'], auth=(arg['username'], arg['password']))
        imageHref = json.loads(snapshotImageRequest.text)['image_href']
        if imageHref:
            hipster.method('rooms/message', method='POST', parameters={'room_id': arg['hipchatroomid'], 'from': 'Librato', 'message':"<img src='{0}' />".format(imageHref) })
            readyImage = True
        else:
            time.sleep(1)

    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', dest='username', default=os.environ.get('LIBRATO_USERNAME'), help='Librato Username')
    parser.add_argument('-p', '--password', dest='password', default=os.environ.get('LIBRATO_PASSWORD'), help='Librato Password')
    parser.add_argument('-d', '--duration', dest='duration', default=os.environ.get('LIBRATO_METRIC_DURATION'), help='Librato Metric Duration')
    parser.add_argument('-ct', '--charttype', dest='charttype', default=os.environ.get('LIBRATO_METRIC_CHART_TYPE'), help='Librato Metric Chart Type')
    parser.add_argument('-ci', '--chartid', dest='chartid', default=os.environ.get('LIBRATO_METRIC_CHART_Id'), help='Librato Metric Chart Id')
    parser.add_argument('-ht', '--hipchattoken', dest='hipchattoken', default=os.environ.get('HIPCHAT_TOKEN'), help='Hipchat Token')
    parser.add_argument('-hri', '--hipchatroomid', dest='hipchatroomid', default=os.environ.get('HIPCHAT_ROOM_ID'), help='Hipchat Room Id')



    args = parser.parse_args()
    main(**vars(args))