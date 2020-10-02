"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from pathlib import Path
from os import stat as os_stat
from os import path as os_path


class Main(TestCase):
    __test__ = False

    def test(self):
        # print(self.__class__.__name__)
        if self.__class__.__name__ == 'Main':
            self.skipTest('Generic Class')
        else:
            self._preexec  ()
            self._run      ()
            self._postexec ()
            self._check    ()

    def _preexec(self):
        pass

    def _check(self):
        self._check_files_hashes('sha512')

    def _get_func_from_name(self, name):
        try:
            if self.obj:
                return getattr(self.obj, name)
        except AttributeError:
            try:
                if self.cls_name:
                    cls  = getattr(__import__(self.mod_name, fromlist=[self.cls_name]), self.cls_name)
                    return getattr(cls, name)
            except AttributeError:
                return getattr(__import__(self.mod_name), name)

    def _run(self):
        Main._run_module_func(self._get_func_from_name(self.func_name), self.args)

    def _postexec(self):
        pass

    def _check_files_hashes(self, hash_func):
        for file, hash in self.files:
            self.assertTrue(Main._check_file_hash(file, hash, hash_func))

    def _check_files_size(self):
        for file, size in self.files:
            self.assertTrue(Main._check_file_size(file, size))

    def _check_files_exist(self):
        for file, size in self.files:
            self.assertTrue(os_path.exists(file))
            self.assertGreater(os_stat(file).st_size, 0)

    @staticmethod
    def _check_content_hash(content, hash, hash_func='sha256'):
        module = __import__('hashlib')
        func = getattr(module, hash_func)

        print()
        print('-- HASH')
        print('computed: ', func(content.encode()).hexdigest())
        print('stored:   ', hash)
        print('--')
        return func(content.encode()).hexdigest() == hash

    @staticmethod
    def _check_file_hash(file, hash, hash_func='sha256'):
        module = __import__('hashlib')
        func = getattr(module, hash_func)

        print()
        print(file)
        print('-- HASH')
        print('computed: ', func(Path(file).read_bytes()).hexdigest())
        print('stored:   ', hash)
        print('--')
        return func(Path(file).read_bytes()).hexdigest() == hash

    @staticmethod
    def _check_file_size(file, size):
        print()
        print(file)
        print('-- SIZE')
        s = os_stat(file).st_size
        print('computed: ', s)
        print('stored:   ', size)
        print('--')
        return s == size

    # def _check_files(self):
    #     for file, hash in self.hashes:
    #         print()
    #         print(file)
    #         self.assertTrue(os_path.exists(file))

    @staticmethod
    def _sort_file(filename):
        with open(filename, 'r') as f:
            out_full_react = ''.join(sorted(f.readlines()))
        with open(filename, 'w') as f:
            f.write(out_full_react)

    @staticmethod
    def _run_module_func(func, args):
        func(args)
