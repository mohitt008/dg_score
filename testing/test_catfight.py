import requests, json, csv, time
import pytest

from requests.auth import HTTPBasicAuth

HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}
URI='localhost'
#URI= 'stg-api.delhivery.io'
CID_URL = 'http://{}/done-services/catfight/input'.format(URI)
RESULTS_URL = 'http://{}/done-services/catfight/results'.format(URI)

COMBINED_URL = 'http://{}/done-services/input'.format(URI)

AUTH = HTTPBasicAuth('done','done@123') 
QA_AUTH = HTTPBasicAuth('qa','qa@delhivery@123') 

INPUT_ADDRESS_FILE = "input.csv"
RESULT_ADDRESS_FILE = "output.csv"
payload = []

def catfight_get_cid(data):
    r = requests.post(CID_URL, data = json.dumps(data), headers = HEADERS,
                auth = AUTH, verify = False) 
    return r

def catfight_get_results(cid):
    #print (cid)
    r = requests.get(RESULTS_URL, auth = AUTH, data = json.dumps(cid),
                            headers = HEADERS, verify = False)
    return r

def fest_server():
    data = {'wbn': '7678', 'prd': 'apple iphone 6s 8gb'}
    r = requests.post(CID_URL, data = json.dumps(data), headers = HEADERS,
                auth = AUTH, verify = False)
    if r.status_code == 500 :
        print ("server error")
    assert r.status_code != 500

def test_auth():
    data = {'wbn': '7678', 'prd': 'apple iphone 6s 8gb'}
    r = requests.post(CID_URL, data = json.dumps(data), headers = HEADERS,
                auth = AUTH, verify = False)
    if r.status_code == 401:
        print ("auth fail")
    assert r.status_code != 401

def fest_combined():
    data = [{'wbn': '7678', 'prd': 'apple iphone 6s 8gb', 'type': 1}]
    r = requests.post(COMBINED_URL, data = json.dumps(data), headers = HEADERS,
                auth = QA_AUTH, verify = False)
    if r.status_code == 500 :
        print ("done error")
    assert r.status_code == 200


@pytest.mark.parametrize("input, input_status, output_status", [
    ({'wbn': '7678', 'prd': 'apple iphone 6s 8gb'}, 202, 200),
    ({'wbn': '7678', 'prd': 'how are you'}, 202, 200),
    ([], 400, 400),
    ({'wbn': ''}, 202, 200),
    ({'wbn' : '7487', 'prd' : 'Yepme Men-Brown Slip On Shoes'}, 202, 200),
    ({'wbn' : '23346748', 'prd' : 'Fonokase Universal Screen Protector for Nokia C6'}, 202, 200),
    ({'wbn' : '635732', 'prd' : 'Green Printed Short Kurta,'}, 202, 200),
    ({'wbn' : '2311190', 'prd' : 'Levi\'S Black Levis Hourglass Jeans (Size: 32)'}, 202, 200),
])

def test_input_results(input, input_status, output_status, capsys):
    input_response = catfight_get_cid(input)
    cid = input_response.json()
    out, err = capsys.readouterr()
    assert input_response.status_code == input_status
    assert catfight_get_results(cid).status_code == output_status

def test_csv():
    f = open(INPUT_ADDRESS_FILE)
    reader = csv.reader(f)
    keys = reader.next()

    f2 = open(RESULT_ADDRESS_FILE, 'w')

    l = ['wbn', 'prd', 'cat', 'scat', 'dg', 'cached']

    writer = csv.DictWriter(f2, fieldnames = l)
    writer.writeheader()

    num_cache = 0
    cnt = 0
    error_input = []
    error_results = []
    for row in reader:
        max_retry = 0
        payload = []
        record_dict = {}
        
        cnt += 1
        
        try:
            for i in range(len(row)):
                record_dict[keys[i]] = row[i]
            payload.append({"wbn":row[0], "prd":row[1]})

            r = catfight_get_cid(payload)
            print r
            
            if r.status_code != 202:
                print "input:http error: ", r.status_code
                error_input.append([payload, r.status_code,r.text] )
                continue
            
            
            cid = r.json()
            
            while max_retry < 5:
                r2 = catfight_get_results(cid)
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
                        error_results.append([payload, r.status_code, r2.status_code, r2.text])
                    max_retry += 1
                    time.sleep(0.1)
            if cnt > 10:
                break

        except Exception as err:
            print('Exception {} against request: {}'.format(err, payload))
            continue
    print len(error_input),len(error_results)
    f.close()
    f2.close()
