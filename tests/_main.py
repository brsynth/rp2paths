"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from hashlib import sha512
from pathlib import Path
from os import path as os_path


class Main(TestCase):
    __test__ = False

    def test(self):
        # print(self.__class__.__name__)
        if self.__class__.__name__ == 'Test_Main':
            self.skipTest('Generic Class')
        else:
            self._preexec  ()
            self._run      ()
            self._postexec ()
            self._check    ()

    def _preexec(self):
        pass

    def _get_func_from_name(self, name):
        if self.cls_name:
            cls  = getattr(__import__(self.mod_name, fromlist=[self.cls_name]), self.cls_name)
            return getattr(cls, name)
        else:
            return getattr(self.mod_name, name)

    def _run(self):
        Main._run_module_func(self._get_func_from_name(self.func_name), self.args)

    def _postexec(self):
        pass

    def _check_hashes(self):
        for file, hash in self.hashes:
            self.assertTrue(Main._check_file_hash(file, hash))

    @staticmethod
    def _check_file_hash(file, hash):
        print()
        print(file)
        print('-- HASH')
        print('computed: ', sha512(Path(file).read_bytes()).hexdigest())
        print('stored:   ', hash)
        print('--')
        return sha512(Path(file).read_bytes()).hexdigest() == hash

    def _check_files(self):
        for file, hash in self.hashes:
            print()
            print(file)
            self.assertTrue(os_path.exists(file))

    @staticmethod
    def _sort_file(filename):
        with open(filename, 'r') as f:
            out_full_react = ''.join(sorted(f.readlines()))
        with open(filename, 'w') as f:
            f.write(out_full_react)

    @staticmethod
    def _run_module_func(func, args):
        func(args)
