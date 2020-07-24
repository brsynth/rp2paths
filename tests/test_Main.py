"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from rp2paths.RP2paths import build_args_parser, convert, scope, efm, paths, filter, img, dot
from tempfile import TemporaryDirectory
from hashlib import sha512
from pathlib import Path

from time import sleep


# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
class Test_Main(TestCase):

    def setUp(self):
        cmd = 'all data/rp2_pathways.csv --outdir out --timeout 5'.split()
        parser = build_args_parser()
        self.args  = parser.parse_args(cmd)
        self.convert_hashes = {
            self.args.cmpdfile: '3ec79b17620b1f887a15a243a0ae12dd2f4b62cdb4f6f6c2430e585f930000456f51a1ebc6b40bee714ae818c6b95c295ec2ca0cfbcc4160d40b3dcd2d50f3fd',
            self.args.reacfile: '9e2f7d6e8b53f6a687d5a72f18261c89dd44e4bbbc8f3e48542881313d8c2c168999dd929238c8d3a56b68140fb3834b551e0fe0a5f84f572021502850a69a1a',
            self.args.sinkfile: '0d42bbd52aeec14631705d58b4d9ebb339174b314e7aa191ca18085414a81e1fed63bf110f2c0066c5d922c8ccb0dcebfc8c821a7e2c76cfead4926f94c4f5c3',
        }
        self.scope_hashes = {
            'out_comp':       '4293088b91b07d7ec62b559ba2bc42c2580cc5a6a5243e93e54772985df494c0fa8319deb470b63df2a4131440bf6c27e43348c5b6e8784f6fb85333904c8bce',
            'out_discarded':  'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e',
            'out_full_react': '9e2f7d6e8b53f6a687d5a72f18261c89dd44e4bbbc8f3e48542881313d8c2c168999dd929238c8d3a56b68140fb3834b551e0fe0a5f84f572021502850a69a1a',
            'out_info':       '7f9ef2b9a1ae08d99578b6cea689f8b0f6b0e2de447489c8e86e6505f2d024d00849c06c6365533d7e0aacc718cbf9b856f4aceafd2870f92c4abe5e866ba867',
            'out_mat':        '9b56f926bc54242fe41abbfbbce3e51daa552564f02d205f8ec5bee8112a4e608d631aa93fcb919b3dc472c265122d629b1f6a716621417ab3d823e6b1a7130e',
            'out_react':      'cdb3ea1bb66c6ebe5930efd5c494ec19cf4773f6fd559b0e21365f8834837dc30baf9bba0cab3c78c4fb99364a4c4a670b7785576c0e46a8820e0eb6fa7722bd',
            'out_rever':      '196aad1afd3f99d88c2aa90abdaed338e06f87f15dbdd62a92d210c7e22878f47b9aefdb037dcc97b75ec02630f7e7ef4c7598b92e18db176cea403730769ff5'
        }
        self.efm_hashes = {
            'out_efm': '0d00689592d509fcac600ccc354683700d329518a343fe140977d43ba7857c5c64b664702ec07f907bafb592ebdd48fdd6a57fae0dd3b754e6aff1018e8aafa2',
        }
        self.paths_hashes = {
            'out_paths.csv': '82bcf321b25fd3222adb7b3e80734e83e9d5053fa306d809cb143db5667483f91925732c7fdb740dc099ee931370cd2d1abcbb748084fe0be912e9daf85d0c21',
        }

    def _check_files(self, func):
        hashes = getattr(self, func+'_hashes')
        for file in list(hashes.keys()):
            self.assertEqual(
                sha512(Path(self.args.outdir+'/'+file).read_bytes()).hexdigest(),
                hashes[file])

    def test_convert(self):
        convert(self.args)
        self._check_files('convert')

    def test_scope(self):
        scope(self.args)
        # 'out_full_react' contains a dict so the order is different each run.
        # In order to check that the content is correct,
        # the file has to be re-written with sorted content
        with open('out/out_full_react', 'r') as f:
            out_full_react = ''.join(sorted(f.readlines()))
        with open('out/out_full_react', 'w') as f:
            f.write(out_full_react)
        self._check_files('scope')

    def test_efm(self):
        self.test_scope()
        efm(self.args)
        self._check_files('efm')

    def test_paths(self):
        paths(self.args)
        self._check_files('paths')

    # def test_filter(self):
    #     self.test_scope()
    #     self.test_efm()
    #     self.test_paths()
    #     filter(self.args)
    #     # sleep(60)
    #     self._check_files('scope')
    #     self._check_files('efm')
    #     self._check_files('paths')
    #     # self._check_files('filter')

    def test_img(self):
        self.test_scope()
        self.test_efm()
        self.test_paths()
        img(self.args)
        sleep(60)
        self._check_files('img')

    # def test_dot(self):
    #     paths(self.args)
    #     sleep(60)
    #     self._check_files('dot')
