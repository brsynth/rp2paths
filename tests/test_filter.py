"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from os import path as os_path
from module import module

files = {
    os_path.join(module.args.outdir, 'out_full_react'): '6c27133dd6cad5285c9141a0756ebb331f94384fd1ca06963c36fc7a63889c84dc0bf488c48d29cea7d463af5e721de13891311c8e872beda644dc3782b27f5a',
}
files = list(files.items())
parent_test = 'paths'


class Test_Filter(module):
    __test__ = True

    func_name = 'filter'
    files = files

    def _postexec(self):
        # 'out_full_react' contains a dict so the order is different each run.
        # In order to check that the content is correct,
        # the file has to be re-written with sorted content
        for file, hash in self.files:
            module._sort_file(file)
