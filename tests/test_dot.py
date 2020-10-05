"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from module import module


files = {
module.args.outdir+'/'+module.args.dotfilebase+'1.dot': 1266,
module.args.outdir+'/'+module.args.dotfilebase+'10.dot': 1343,
module.args.outdir+'/'+module.args.dotfilebase+'11.dot': 1552,
module.args.outdir+'/'+module.args.dotfilebase+'12.dot': 1769,
module.args.outdir+'/'+module.args.dotfilebase+'13.dot': 1560,
module.args.outdir+'/'+module.args.dotfilebase+'14.dot': 1288,
module.args.outdir+'/'+module.args.dotfilebase+'15.dot': 1559,
module.args.outdir+'/'+module.args.dotfilebase+'16.dot': 1560,
module.args.outdir+'/'+module.args.dotfilebase+'17.dot': 1560,
module.args.outdir+'/'+module.args.dotfilebase+'18.dot': 1559,
module.args.outdir+'/'+module.args.dotfilebase+'19.dot': 1554,
module.args.outdir+'/'+module.args.dotfilebase+'2.dot': 1004,
module.args.outdir+'/'+module.args.dotfilebase+'20.dot': 1551,
module.args.outdir+'/'+module.args.dotfilebase+'21.dot': 1554,
module.args.outdir+'/'+module.args.dotfilebase+'22.dot': 1779,
module.args.outdir+'/'+module.args.dotfilebase+'23.dot': 2116,
module.args.outdir+'/'+module.args.dotfilebase+'24.dot': 1899,
module.args.outdir+'/'+module.args.dotfilebase+'25.dot': 2116,
module.args.outdir+'/'+module.args.dotfilebase+'26.dot': 2289,
module.args.outdir+'/'+module.args.dotfilebase+'27.dot': 2291,
module.args.outdir+'/'+module.args.dotfilebase+'28.dot': 2282,
module.args.outdir+'/'+module.args.dotfilebase+'29.dot': 2059,
module.args.outdir+'/'+module.args.dotfilebase+'3.dot': 1266,
module.args.outdir+'/'+module.args.dotfilebase+'30.dot': 1837,
module.args.outdir+'/'+module.args.dotfilebase+'4.dot': 1772,
module.args.outdir+'/'+module.args.dotfilebase+'5.dot': 1551,
module.args.outdir+'/'+module.args.dotfilebase+'6.dot': 1768,
module.args.outdir+'/'+module.args.dotfilebase+'7.dot': 1559,
module.args.outdir+'/'+module.args.dotfilebase+'8.dot': 1334,
module.args.outdir+'/'+module.args.dotfilebase+'9.dot': 1551,
}
files = list(files.items())
parent_test = 'img'

class Test_Dot(module):
    __test__ = True

    func_name = 'dot'
    files = files

    def _check(self):
        self._check_files_size()
