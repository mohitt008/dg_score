import json,requests,csv,time
from requests.auth import HTTPBasicAuth

INPUT_ADDRESS_FILE = "input.csv"
RESULT_ADDRESS_FILE = "output.csv"

HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

URI='done.delhivery.io'

CID_URL = 'http://{}/done-services/catfight/input'.format(URI)
RESULTS_URL = 'http://{}/done-services/catfight/results'.format(URI)

AUTH = HTTPBasicAuth('done','delhivery@123')

f = open(INPUT_ADDRESS_FILE)
reader = csv.reader(f)
keys = reader.next()

f2 = open(RESULT_ADDRESS_FILE, 'w')

l = ['wbn', 'prd', 'cat', 'scat', 'dg', 'cached']

writer = csv.DictWriter(f2, fieldnames = l)
writer.writeheader()

num_cache = 0
cnt = 0

for row in reader:
    max_retry = 0
    payload = []
    record_dict = {}
    
    cnt += 1
    
    try:
        for i in range(len(row)):
            record_dict[keys[i]] = row[i]
        payload.append({"wbn":row[0], "prd":row[1]})

        r = requests.post(CID_URL, data = json.dumps(payload), headers = HEADERS,
                        auth = AUTH, verify = False)
        
        if r.status_code != 202:
            print "input:http error: ", r.status_code
            continue
        
        print r.json()
        cid = r.json()
        
        while max_retry < 5:
            r2 = requests.get(RESULTS_URL, auth = AUTH, data = json.dumps(cid),
                            headers = HEADERS, verify = False)
            if r2.status_code == 200:
                res = r2.json()
                res = res[0]['result']
                x = {}
                x['wbn'] = record_dict['wbn']
                x['prd'] = record_dict['prd'],
                
                x['cat'] = res['cat']
                x['scat'] = res['scat']
                x['dg'] = res['dg']
                x['cached'] = res['cached']

                if x['cached']:
                    num_cache += 1
            
                writer.writerow(x)
                break
            else:
                if r2.status_code != 202:
                    print "results:http error ", r2.status_code
                    print "results: error ", r2.text
                max_retry += 1
                time.sleep(0.1)

        if cnt > 5:
            break

    except Exception as err:
        print('Exception {} against request: {}'.format(err, payload))
        continue

f.close()
f2.close()
#print num_cache

