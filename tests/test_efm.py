"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from module import module

files = [
    (module.args.outdir+'/'+'out_efm', '0d00689592d509fcac600ccc354683700d329518a343fe140977d43ba7857c5c64b664702ec07f907bafb592ebdd48fdd6a57fae0dd3b754e6aff1018e8aafa2'),
]
parent_test = 'scope'



class Test_Efm(module):
    __test__ = True

    func_name = 'efm'
    files = files
