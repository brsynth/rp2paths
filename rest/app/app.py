"""
Created on March 7 2019

@author: Melchior du Lac
@description: Standalone version of RP2paths. Returns bytes to be able to use the same file in REST application

"""
import subprocess
import tempfile
import logging
import resource
import glob
# import io
# import tarfile
# #from flask import Flask, request, jsonify, send_file, abort
# from flask import request, Response, send_file
# import json

MAX_VIRTUAL_MEMORY = 20000 * 1024 * 1024 # 20GB -- define what is the best
#MAX_VIRTUAL_MEMORY = 20 * 1024 * 1024 # 20GB -- define what is the best

##
#
#
def limit_virtual_memory():
    resource.setrlimit(resource.RLIMIT_AS, (MAX_VIRTUAL_MEMORY, resource.RLIM_INFINITY))

import io
import tarfile
def tar_cz_relative(*path):
    """tar_cz(*path) -> bytes
    Compress a sequence of files or directories in memory.
    The resulting string could be stored as a .tgz file."""
    file_out = io.BytesIO()
    tar = tarfile.open(mode = "w:gz", fileobj = file_out)
    for p in path:
        tar.add(p, arcname='./')
    tar.close()
    return file_out.getvalue()

##
#
#
#def run(rp2_pathways_bytes, timeout, logger=None):
def run(args):
#    if logger==None:

    if args['logger']==None:
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)

    out_paths = b''
    out_compounds = b''

    with tempfile.TemporaryDirectory() as tmpOutputFolder:

        rp2_pathways = tmpOutputFolder+'/tmp_rp2_pathways.csv'
        with open(tmpOutputFolder+'/tmp_rp2_pathways.csv', 'wb') as outfi:
            outfi.write(args['bytes'])

        rp2paths_command = 'python3 /home/src/RP2paths.py all '+str(rp2_pathways)+' --outdir '+str(tmpOutputFolder)+' --timeout '+str(int(args['timeout']*60.0+10.0))

        try:
            commandObj = subprocess.Popen(rp2paths_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=limit_virtual_memory)

            try:
                commandObj.wait(timeout=args['timeout']*60.0)
            except subprocess.TimeoutExpired as e:
                logger.error('Timeout from rp2paths ('+str(timeout)+' minutes)')
                commandObj.kill()
                return b'', b'', b'timeout', str.encode('Command: '+str(rp2paths_command)+'\n Error: '+str(e)+'\n tmpfolder: '+str(glob.glob(tmpfolder+'/*')))
            (result, error) = commandObj.communicate()
            result = result.decode('utf-8')
            error = error.decode('utf-8')
            #TODO test to see what is the correct phrase
            if 'failed to map segment from shared object' in error:
                logger.error('RP2paths does not have sufficient memory to continue')
                return b'', b'', b'memoryerror', str.encode('Command: '+str(rp2paths_command)+'\n Error: '+str(error)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*')))

            ### Return an compressed archive of result files ###
            try:

                return tar_cz_relative(tmpOutputFolder)

            except FileNotFoundError as e:
                logger.error('Cannot find the output folder'+tmpOutputFolder)
                return b'', b'', b'filenotfounderror', str.encode('Command: '+str(rp2paths_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*')))

        except OSError as e:
            logger.error('Subprocess detected an error when calling the rp2paths command')
            return b'', b'', b'oserror', str.encode('Command: '+str(rp2paths_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*')))

        except ValueError as e:
            logger.error('Cannot set the RAM usage limit')
            return b'', b'', b'valueerror', str.encode('Command: '+str(rp2paths_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*')))



from flask import request, send_file
import io
import json


def post(rest_query):

    outTar = None

    rp2_pathways_bytes = request.files['rp2_pathways'].read()
    params = json.load(request.files['data'])
    args = {'bytes': rp2_pathways_bytes,
            'timeout': params['timeout'],
            'galaxy': params['galaxy'],
            'logger': None}

    result_bytes = rest_query.run(args)

    #######################
    return send_file(io.BytesIO(result_bytes), as_attachment=True, attachment_filename='rp2paths_result.tar.gz', mimetype='application/gzip')
