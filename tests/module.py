"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from _main import Main
from os import path as os_path


class module(Main):
    __test__ = False

    mod_name = 'rp2paths'
    cls_name = 'RP2paths'
    infile = os_path.join('data', 'rp2_pathways.csv')
    out_folder = os_path.join(os_path.dirname(os_path.realpath(__file__)), 'out')
    cmd  = str(f'all {infile} --outdir {out_folder}').split()
    bap  = getattr(__import__(mod_name), 'build_args_parser')
    args = bap().parse_args(cmd)


    def _preexec(self):

        preexec_func_names = self._list_preexec_func_names()

        for preexec_func_name in preexec_func_names:

            legacy_files = getattr(__import__('test_'+preexec_func_name), 'files')

            for file, hash in legacy_files:
                if not os_path.isfile(file):
                    func = self._get_func_from_name(preexec_func_name)
                    self.args.func = func
                    # print('HISTORY: ', func)
                    Main._run_module_func(func, self.args)


    def _list_preexec_func_names(self):

        preexec_func_names = []

        parent_test = getattr(__import__('test_'+self.func_name), 'parent_test')

        while parent_test:
            # prepend
            preexec_func_names.insert(0, parent_test)
            parent_test = getattr(__import__('test_'+parent_test), 'parent_test')

        return preexec_func_names
