"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from os import path as os_path
from module import module


files = [
    (os_path.join(module.args.outdir, 'out_comp'),       'fa781b809c48c38a0c525be1b9d1ada93a3bd6dc732d784cc4d5ed1c466a3b4f57989c4f618a9e5eec8190f4da9d68999ef89e45b2777b3695042f432dec9a3e'),
    (os_path.join(module.args.outdir, 'out_discarded'),  'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e'),
    (os_path.join(module.args.outdir, 'out_full_react'), '6c27133dd6cad5285c9141a0756ebb331f94384fd1ca06963c36fc7a63889c84dc0bf488c48d29cea7d463af5e721de13891311c8e872beda644dc3782b27f5a'),
    (os_path.join(module.args.outdir, 'out_info'),       'ec00649b978ca2eca14c680831d802886f1d034a436b47ef6220c6af3b458e968f3ac61b511857cb06c9bc37b98f45ca6d1c674a5d084229475c160d1723eae5'),
    (os_path.join(module.args.outdir, 'out_mat'),        '933305f24c31005e3518e109cd606a362b48fbd6cb4755ce40b1120f7c10638cda6edb09ee749914024bf24ed3bec426d1ec273fa9085585a2637057fb258ca6'),
    (os_path.join(module.args.outdir, 'out_react'),      'd5fd060540d23bf7cf9aa56f48ef9fa5cc448938315427214e6ec7f2b022a126de0ff123211effa4c072f09e348e3eef68e3fc4f200161809cd4fafb9aa1501e'),
    (os_path.join(module.args.outdir, 'out_rever'),      'd4f517a79fcc7959ccb19381a57468294ef07517cdc4e753e38fe01f96949b323480a5ab1fb07ef90a27af1c12458e53bd5a8d07df4bba82bf72089b15012077')
]
parent_test = 'convert'



class Test_Scope(module):
    __test__ = True

    func_name = 'scope'
    files = files

    def _postexec(self):
        # 'out_full_react' contains a dict so the order is different each run.
        # In order to check that the content is correct,
        # the file has to be re-written with sorted content
        module._sort_file(os_path.join(module.args.outdir, 'out_full_react'))
