"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from module import module

files = [
        (module.args.outdir+'/'+module.args.pathsfile, '82bcf321b25fd3222adb7b3e80734e83e9d5053fa306d809cb143db5667483f91925732c7fdb740dc099ee931370cd2d1abcbb748084fe0be912e9daf85d0c21'),
]
parent_test = 'efm'


class Test_Paths(module):
    __test__ = True

    func_name = 'paths'
    files = files
