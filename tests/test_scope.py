"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from module import module


files = [
    (module.args.outdir+'/'+'out_comp',       '4293088b91b07d7ec62b559ba2bc42c2580cc5a6a5243e93e54772985df494c0fa8319deb470b63df2a4131440bf6c27e43348c5b6e8784f6fb85333904c8bce'),
    (module.args.outdir+'/'+'out_discarded',  'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e'),
    (module.args.outdir+'/'+'out_full_react', '9e2f7d6e8b53f6a687d5a72f18261c89dd44e4bbbc8f3e48542881313d8c2c168999dd929238c8d3a56b68140fb3834b551e0fe0a5f84f572021502850a69a1a'),
    (module.args.outdir+'/'+'out_info',       '7f9ef2b9a1ae08d99578b6cea689f8b0f6b0e2de447489c8e86e6505f2d024d00849c06c6365533d7e0aacc718cbf9b856f4aceafd2870f92c4abe5e866ba867'),
    (module.args.outdir+'/'+'out_mat',        '9b56f926bc54242fe41abbfbbce3e51daa552564f02d205f8ec5bee8112a4e608d631aa93fcb919b3dc472c265122d629b1f6a716621417ab3d823e6b1a7130e'),
    (module.args.outdir+'/'+'out_react',      'cdb3ea1bb66c6ebe5930efd5c494ec19cf4773f6fd559b0e21365f8834837dc30baf9bba0cab3c78c4fb99364a4c4a670b7785576c0e46a8820e0eb6fa7722bd'),
    (module.args.outdir+'/'+'out_rever',      '196aad1afd3f99d88c2aa90abdaed338e06f87f15dbdd62a92d210c7e22878f47b9aefdb037dcc97b75ec02630f7e7ef4c7598b92e18db176cea403730769ff5')
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
        module._sort_file(module.args.outdir+'/'+'out_full_react')
