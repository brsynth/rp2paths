"""
Created on Jul 15 2020

@author: Joan Hérisson
"""
from os import path as os_path
from module import module

files = [
    (
        os_path.join(
            module.args.outdir,
            'out_efm'
        ),
        'a2c257b1f5cf10b26f4eeb62e93ad70d835e7e3d840fcb054cd4024d9df5392481e0735850fe0c979bfe43ac5b77b40d9494a28e99afe256dfa66bdc1ed2a8df'
    ),
]
parent_test = 'scope'



class Test_Efm(module):
    __test__ = True

    func_name = 'efm'
    files = files
