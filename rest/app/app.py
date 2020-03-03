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
        #rp2paths_command = ['python', '/home/RP2paths.py', 'all', rp2_pathways, '--outdir', tmpOutputFolder, '--timeout', str(timeout)]
        rp2paths_command = 'python3 /home/src/RP2paths.py all '+str(rp2_pathways)+' --outdir '+str(tmpOutputFolder)+' --timeout '+str(int(args['timeout']*60.0+10.0))
#        rp2paths_command = 'find / -name tmp_rp2_pathways.csv'
        try:
            commandObj = subprocess.Popen(rp2paths_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=limit_virtual_memory)
            #commandObj = subprocess.Popen(rp2paths_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, preexec_fn=limit_virtual_memory)
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
            ### convert the result to binary and return ###
            try:
                with open(tmpOutputFolder+'/out_paths.csv', 'rb') as op:
                    out_paths = op.read()
                with open(tmpOutputFolder+'/compounds.txt', 'rb') as c:
                    out_compounds = c.read()
                return out_paths, out_compounds, b'noerror', b''
            except FileNotFoundError as e:
                logger.error('Cannot find the output files out_paths.csv or compounds.txt')
                return b'', b'', b'filenotfounderror', str.encode('Command: '+str(rp2paths_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*')))
        except OSError as e:
            logger.error('Subprocess detected an error when calling the rp2paths command')
            return b'', b'', b'oserror', str.encode('Command: '+str(rp2paths_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*')))
        except ValueError as e:
            logger.error('Cannot set the RAM usage limit')
            return b'', b'', b'valueerror', str.encode('Command: '+str(rp2paths_command)+'\n Error: '+str(e)+'\n tmpOutputFolder: '+str(glob.glob(tmpOutputFolder+'/*')))



from flask import request, Response, send_file
import io
import tarfile
import json
import logging

def post(rest_query):
    outTar = None
    rp2_pathways_bytes = request.files['rp2_pathways'].read()
    params = json.load(request.files['data'])
    args = {'bytes': rp2_pathways_bytes, 'timeout': params['timeout'], 'logger': None}
    result = rest_query.run(args)
    if result[2]==b'filenotfounderror':
        return Response("FileNotFound Error from rp2paths \n "+str(result[3]), status=400)
    if result[2]==b'oserror':
        return Response("rp2paths has generated an OS error \n"+str(result[3]), status=400)
    if result[2]==b'memerror':
        return Response("Memory allocation error \n"+str(result[3]), status=400)
    if result[0]==b'' and result[1]==b'':
        return Response("Could not find any results \n"+str(result[3]), status=400)
    if result[2]==b'valueerror':
        return Response("Could not setup a RAM limit \n"+str(result[3]), status=400)
    outTar = io.BytesIO()
    with tarfile.open(fileobj=outTar, mode='w:xz') as tf:
        #make a tar to pass back to the rp2path flask service
        out_paths = io.BytesIO(result[0])
        out_compounds = io.BytesIO(result[1])
        #out_paths = result[0]
        #out_compounds = result[1]
        info = tarfile.TarInfo(name='rp2paths_pathways')
        info.size = len(result[0])
        tf.addfile(tarinfo=info, fileobj=out_paths)
        info = tarfile.TarInfo(name='rp2paths_compounds')
        info.size = len(result[1])
        tf.addfile(tarinfo=info, fileobj=out_compounds)
    ###### IMPORTANT ######
    outTar.seek(0)
    #######################
    return send_file(outTar, as_attachment=True, attachment_filename='rp2paths_result.tar', mimetype='application/x-tar')
