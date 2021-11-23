"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from os import path as os_path
from module import module

files = [
    (os_path.join(module.args.outdir, module.args.pathsfile), '58961c5a1e58d4ca320121e02374718cafc05163e643de2c7a41e7c51baa14f1d6082608feebcba2d8347df459f44c3aa531d3e34e43a8d517ad45e67e09e519'),
]
parent_test = 'efm'


class Test_Paths(module):
    __test__ = True

    func_name = 'paths'
    files = files
