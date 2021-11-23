"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from os import path as os_path
from module import module

files = {
    os_path.join(
        module.args.outdir,
        module.args.cmpdfile
    ): 'c17ce779ba4b9fd99f01e2e4d00ec728c44af3529d4a654b0f1eb2676b1c49cba21855b0896c4f4d1ba48a7b86d62f7c3801114ae991b6fd0ec08bc2d4be0de1',
    os_path.join(
        module.args.outdir,
        module.args.reacfile
    ): '6c27133dd6cad5285c9141a0756ebb331f94384fd1ca06963c36fc7a63889c84dc0bf488c48d29cea7d463af5e721de13891311c8e872beda644dc3782b27f5a',
    os_path.join(
        module.args.outdir,
        module.args.sinkfile
    ): '6d0d3652696ca6d043541a57279214c00e91754ac14b05f05cc62c7221cde503f8b4f7de4cb29d882540bd2bd2cee7a71cb50d1fcace06073e550ef2bb98dfef',
}
files = list(files.items())
parent_test = ''


class Test_Convert(module):
    __test__ = True

    func_name = 'convert'
    files = files
