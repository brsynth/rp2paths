"""
Created on Oct 16 2023

@author: Joan Hérisson
"""

from unittest import TestCase

from os import stat as os_stat
from os import path as os_path

from rp2paths.rp2erxn import Compound


class Test_rp2erxn(TestCase):

    def test_SortCidsMNXM_1(self):
        mnx_cids = ['MNXM03', 'MNXM02', 'MNXM5', 'MNXM1']
        self.assertListEqual(
            Compound.SortCids(mnx_cids),
            ['MNXM1', 'MNXM02', 'MNXM03', 'MNXM5']
        )

    def test_SortCidsMNXM_2(self):
        mnx_cids = ['MNXM03', 'MNXM02', 'MNXM5__64__MNXC3', 'MNXM1']
        self.assertListEqual(
            Compound.SortCids(mnx_cids),
            ['MNXM1', 'MNXM02', 'MNXM03', 'MNXM5__64__MNXC3']
        )

    def test_SortCidsNotMNXM(self):
        mnx_cids = ['M_2agpg181_c', 'M_2agpg161_c', 'M_2ahbut_c', 'M_2agpg180_c', 'MNXM1']
        self.assertListEqual(
            Compound.SortCids(mnx_cids),
            ['MNXM1', 'M_2agpg161_c', 'M_2agpg180_c', 'M_2agpg181_c', 'M_2ahbut_c']
        )
