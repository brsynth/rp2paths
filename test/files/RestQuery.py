#!/usr/bin/env python3

import argparse
import io
import tarfile
import json
import requests
import logging

# Wrapper for the RP2paths script that takes the same input (results.csv) as the original script but returns
# the out_paths.csv so as to be compliant with Galaxy

def rp2pathsUpload(rp2_pathways, rp2paths_pathways, rp2paths_compounds, timeout, server_url):
    # Post request
    data = {'timeout': timeout}
    files = {'rp2_pathways': open(rp2_pathways, 'rb'),
            'data': ('data.json', json.dumps(data))}
    try:
        r = requests.post(server_url+'/Query', files=files)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        logging.error(r.text)
        return False
    #r.raise_for_status()
    return_content = r.content
    filelike = io.BytesIO(return_content)
    with tarfile.open(fileobj=filelike, mode='r:xz') as tf:
        with open(rp2paths_pathways, 'wb') as rpp:
            rpp.write(tf.extractfile(tf.getmember('rp2paths_pathways')).read())
        with open(rp2paths_compounds, 'wb') as rpc:
            rpc.write(tf.extractfile(tf.getmember('rp2paths_compounds')).read())


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Python wrapper for the python RP2paths script')
    parser.add_argument('-rp2_pathways', type=str)
    parser.add_argument('-rp2paths_pathways', type=str)
    parser.add_argument('-rp2paths_compounds', type=str)
    parser.add_argument('-timeout', type=int)
    parser.add_argument('-server_url', type=str)
    params = parser.parse_args()
    rp2pathsUpload(params.rp2_pathways, params.rp2paths_pathways, params.rp2paths_compounds, params.timeout, params.server_url)
