"""
Created on Jul 15 2020

@author: Joan Hérisson
"""
from os import path as os_path
from module import module


files = {
os_path.join(module.args.outdir, module.args.dotfilebase+'1.dot'): 1250,
os_path.join(module.args.outdir, module.args.dotfilebase+'10.dot'): 1325,
os_path.join(module.args.outdir, module.args.dotfilebase+'11.dot'): 1532,
os_path.join(module.args.outdir, module.args.dotfilebase+'12.dot'): 1747,
os_path.join(module.args.outdir, module.args.dotfilebase+'13.dot'): 1540,
os_path.join(module.args.outdir, module.args.dotfilebase+'14.dot'): 1271,
os_path.join(module.args.outdir, module.args.dotfilebase+'15.dot'): 1539,
os_path.join(module.args.outdir, module.args.dotfilebase+'16.dot'): 1540,
os_path.join(module.args.outdir, module.args.dotfilebase+'17.dot'): 1540,
os_path.join(module.args.outdir, module.args.dotfilebase+'18.dot'): 1539,
os_path.join(module.args.outdir, module.args.dotfilebase+'19.dot'): 1534,
os_path.join(module.args.outdir, module.args.dotfilebase+'2.dot'): 991,
os_path.join(module.args.outdir, module.args.dotfilebase+'20.dot'): 1531,
os_path.join(module.args.outdir, module.args.dotfilebase+'21.dot'): 1534,
os_path.join(module.args.outdir, module.args.dotfilebase+'22.dot'): 1757,
os_path.join(module.args.outdir, module.args.dotfilebase+'23.dot'): 2089,
os_path.join(module.args.outdir, module.args.dotfilebase+'24.dot'): 1874,
os_path.join(module.args.outdir, module.args.dotfilebase+'25.dot'): 2089,
os_path.join(module.args.outdir, module.args.dotfilebase+'26.dot'): 2261,
os_path.join(module.args.outdir, module.args.dotfilebase+'27.dot'): 2263,
os_path.join(module.args.outdir, module.args.dotfilebase+'28.dot'): 2254,
os_path.join(module.args.outdir, module.args.dotfilebase+'29.dot'): 2033,
os_path.join(module.args.outdir, module.args.dotfilebase+'3.dot'): 1250,
os_path.join(module.args.outdir, module.args.dotfilebase+'30.dot'): 1813,
os_path.join(module.args.outdir, module.args.dotfilebase+'4.dot'): 1750,
os_path.join(module.args.outdir, module.args.dotfilebase+'5.dot'): 1531,
os_path.join(module.args.outdir, module.args.dotfilebase+'6.dot'): 1746,
os_path.join(module.args.outdir, module.args.dotfilebase+'7.dot'): 1539,
os_path.join(module.args.outdir, module.args.dotfilebase+'8.dot'): 1316,
os_path.join(module.args.outdir, module.args.dotfilebase+'9.dot'): 1531,
}
files = list(files.items())
parent_test = 'img'

class Test_Dot(module):
    __test__ = True

    func_name = 'dot'
    files = files

    def _check(self):
        self._check_files_size()
