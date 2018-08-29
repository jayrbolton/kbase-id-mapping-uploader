import requests
import time
import sys

# Base url of the id mapping service endpoint that we are using
_base_url = 'https://ci.kbase.us/services/idmapper/api/v1'


def perform_import(path, auth_token):
    """Iterate over the file, collecting groups of 10000 ids, and making requests to create all mappings."""
    with open(path, 'r') as fd:
        ids = []  # type: list
        iters = 0
        for line in fd.readlines():
            iters += 1
            cols = line.split(' ')
            kbase_id = cols[0]
            refseq_id = cols[1].replace('_assembly', '')
            ids.append((kbase_id, refseq_id))
            if iters >= 10000:
                request_json = ids_to_json(ids)
                make_request(request_json, auth_token)
                ids = []
                iters = 0
        print('final request')
        request_json = ids_to_json(ids)
        make_request(request_json, auth_token)


def ids_to_json(ids):
    """Convert array of pairs of ids into a json object."""
    request_json = ""
    for (id1, id2) in ids:
        request_json += '"%s": "%s",' % (id1, id2)
    # Add braces, get rid of trailing comma
    return "{" + request_json[0:-1] + "}"


def make_request(json, auth_token):
    """
    Given a json request body and a kbase auth token:
    Make the mapping request to the id mapping service.
    """
    endpoint = _base_url + '/mapping/KBase/RefSeq'
    headers = {'Authorization': 'kbase ' + auth_token, 'Content-Type': 'application/json'}
    print('making request to', endpoint)
    print('request body length is', len(json))
    resp = requests.put(endpoint, data=json, headers=headers)
    if not resp.ok:
        print('=' * 80)
        print('status code', resp.status_code)
        print(resp.text)
        raise Exception("Request error (see above).")
    print('response status', resp.status_code)
    return resp


if __name__ == '__main__':
    start = int(time.time() * 1000)
    if len(sys.argv) < 3:
        print('Pass in a file-path as the first argument and an auth token as the second argument.')
        exit(1)
    auth_token = sys.argv[2]
    filepath = sys.argv[1]
    perform_import(filepath, auth_token)
    end = int(time.time() * 1000)
    print('total time in ms: ' + str(end - start))
