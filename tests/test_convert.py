"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from module import module


files = {
    module.args.outdir+'/'+module.args.cmpdfile: '3ec79b17620b1f887a15a243a0ae12dd2f4b62cdb4f6f6c2430e585f930000456f51a1ebc6b40bee714ae818c6b95c295ec2ca0cfbcc4160d40b3dcd2d50f3fd',
    module.args.outdir+'/'+module.args.reacfile: '9e2f7d6e8b53f6a687d5a72f18261c89dd44e4bbbc8f3e48542881313d8c2c168999dd929238c8d3a56b68140fb3834b551e0fe0a5f84f572021502850a69a1a',
    module.args.outdir+'/'+module.args.sinkfile: '0d42bbd52aeec14631705d58b4d9ebb339174b314e7aa191ca18085414a81e1fed63bf110f2c0066c5d922c8ccb0dcebfc8c821a7e2c76cfead4926f94c4f5c3',
}
files = list(files.items())
parent_test = ''


class Test_Convert(module):
    __test__ = True

    func_name = 'convert'
    files = files
