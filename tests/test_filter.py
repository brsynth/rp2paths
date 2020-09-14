"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from module import module

hashes = {
        module.args.outdir+'/'+'out_full_react': '9e2f7d6e8b53f6a687d5a72f18261c89dd44e4bbbc8f3e48542881313d8c2c168999dd929238c8d3a56b68140fb3834b551e0fe0a5f84f572021502850a69a1a',
}
hashes = list(hashes.items())
parent_test = 'paths'

class Test_Filter(module):
    __test__ = True

    func_name = 'filter'
    hashes = hashes

    def _postexec(self):
        # 'out_full_react' contains a dict so the order is different each run.
        # In order to check that the content is correct,
        # the file has to be re-written with sorted content
        module._sort_file('out/out_full_react')

    def _check(self):
        self._check_hashes()
