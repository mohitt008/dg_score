import json
import requests
import time


def request_to_segment_product(payload):
    headers = {'Content-type': 'application/json'}
    url = 'http://stg-api.delhivery.io/category/predict'
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    if r.status_code == 200:
        response = r.json()
        return fetch_queued_request_response(response['cid'])
    else:
        return False
 
 
def fetch_queued_request_response(cid):
    payload = {
        'cid': cid,
    }
    headers = {'Content-type': 'application/json'}
    url = 'http://stg-api.delhivery.io/category/results'
    retry = True
    while retry:
        print('Attempting to fetch data for CID: {}'.format(
            cid))
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        if r.status_code == 200:
            retry = False
            response = r.json()
            return response
        else:
            print('Got a {} status for CID: {}. Sleeping for 2 seconds'.format(
                r.status_code, cid)
            )
            time.sleep(2)
    return False

if __name__ == '__main__':
    print(request_to_segment_product([{'product_name': 'adidas men shoes'}]))