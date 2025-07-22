from unittest import TestCase
from unittest import mock
from unittest.mock import patch as mock_patch
from os import path as os_path
from os import remove as os_remove
from hashlib import sha512
from tempfile import NamedTemporaryFile, TemporaryFile
from json import (
    dump as json_dump,
    load as json_load
)
from pickle import (
    dump as pickle_dump,
    load as pickle_load
)
from brs_utils import create_logger

from rp2paths.RP2paths import TaskCofactors

HERE = os_path.dirname(os_path.abspath(__file__))

class TestCofactors(TestCase):
    def setUp(self):
        self.datadir = os_path.join(HERE, 'data')
        self.inputdir = os_path.join(self.datadir, 'input')
        self.outputdir = os_path.join(self.datadir, 'output')
        self.cofile = os_path.join(self.inputdir, 'empty_sink', 'cofactors_mnx.tsv')
        self.cmpdfile = os_path.join(self.inputdir, 'empty_sink', 'compounds.txt')
        self.reacfile = os_path.join(self.inputdir, 'empty_sink', 'reactions.erxn')
        self.reaclines = open(self.reacfile, 'r').readlines()
        self.cofactors = json_load(open(os_path.join(self.outputdir, 'empty_sink', 'cofactors.json'), 'r'))
        self.compounds_wo_cofactors = json_load(open(os_path.join(self.outputdir, 'empty_sink', 'compounds_wo_cofactors.json'), 'r'))
        self.compdfile_wo_cofactors = os_path.join(self.outputdir, 'empty_sink', 'compounds.txt')
        self.reactions_dict = json_load(open(os_path.join(self.outputdir, 'empty_sink', 'reactions.json'), 'r'))
        self.reactions_wo_cofactors = json_load(open(os_path.join(self.outputdir, 'empty_sink', 'reactions_wo_cofactors.json'), 'r'))
        self.reactions_w_mergedrules = pickle_load(open(os_path.join(self.outputdir, 'empty_sink', 'reactions_w_mergedrules.pkl'), 'rb'))
        self.reacfile_wo_cofactors = os_path.join(self.outputdir, 'empty_sink', 'reactions.erxn')
        self.logger = create_logger('TestCofactors', log_level='INFO')

    def test_read_cofactors(self):
        cofactors = TaskCofactors.read_cofactors(self.cofile)
        # Load expected result from file
        # Compare the cofactors with expected result
        self.assertDictEqual(cofactors, self.cofactors)

    def test_rm_cofactors_in_cmpdfile(self):
        # Copy the cmpdfile to a temporary file to avoid modifying the original
        with NamedTemporaryFile(mode='wb') as temp_cmpdfile:
            with open(self.cmpdfile, 'rb') as src_file:
                while True:
                    chunk = src_file.read(8192)
                    if not chunk:
                        break
                    temp_cmpdfile.write(chunk)
            temp_cmpdfile.seek(0)
            remaining_compounds = TaskCofactors.rm_cofactors_in_cmpdfile(temp_cmpdfile.name, self.cofactors)
            # Compare the remaining compounds with expected result
            self.assertDictEqual(remaining_compounds, self.compounds_wo_cofactors)
            # Compare the written file with expected result
            self.assertEqual(
                open(temp_cmpdfile.name, 'r').read(),
                open(self.compdfile_wo_cofactors, 'r').read()
            )

    def test_dict_from_reacfile(self):
        reac_dict = TaskCofactors.dict_from_reacfile(self.reacfile)
        # Compare the reaction dictionary with expected result
        self.assertDictEqual(reac_dict, self.reactions_dict)

    def test_clean_reactions(self):
        remaining_reactions = TaskCofactors.clean_reactions(self.reactions_dict, self.compounds_wo_cofactors, self.cofactors)
        # Compare the remaining reactions with expected result
        self.assertDictEqual(remaining_reactions, self.reactions_wo_cofactors)

    def test_parse_reacfile(self):
        reacfile_lines = TaskCofactors.parse_reacfile(self.reacfile)
        # Compare the parsed reaction dictionary with expected result
        self.assertEqual(reacfile_lines, self.reaclines)

    def test_merge_reactions_rules(self):
        reac_dict = TaskCofactors.merge_reactions_rules(self.reaclines, self.reactions_wo_cofactors, self.compounds_wo_cofactors)
        # Compare the built reaction dictionary with expected result
        self.assertDictEqual(reac_dict, self.reactions_w_mergedrules)

    @mock_patch('rp2paths.RP2paths.TaskCofactors.read_cofactors', autospec=True)
    @mock_patch('rp2paths.RP2paths.TaskCofactors.rm_cofactors_in_cmpdfile', autospec=True)
    @mock_patch('rp2paths.RP2paths.TaskCofactors.dict_from_reacfile', autospec=True)
    @mock_patch('rp2paths.RP2paths.TaskCofactors.clean_reactions', autospec=True)
    @mock_patch('rp2paths.RP2paths.TaskCofactors.parse_reacfile', autospec=True)
    @mock_patch('rp2paths.RP2paths.TaskCofactors.merge_reactions_rules', autospec=True)
    def test_compute(
        self,
        mock_merge_reactions_rules,
        mock_parse_reacfile,
        mock_clean_reactions,
        mock_dict_from_reacfile,
        mock_rm_cofactors_in_cmpdfile,
        mock_read_cofactors,
    ):
        mock_read_cofactors.return_value = self.cofactors
        mock_rm_cofactors_in_cmpdfile.return_value = self.compounds_wo_cofactors
        mock_dict_from_reacfile.return_value = self.reactions_dict
        mock_clean_reactions.return_value = self.reactions_wo_cofactors
        mock_parse_reacfile.return_value = self.reaclines
        mock_merge_reactions_rules.return_value = self.reactions_w_mergedrules
        # Copy the reacfile to a temporary file to avoid modifying the original
        with NamedTemporaryFile(mode='wb') as temp_reacfile:
            with open(self.reacfile, 'rb') as src_file:
                while True:
                    chunk = src_file.read(8192)
                    if not chunk:
                        break
                    temp_reacfile.write(chunk)
            temp_reacfile.seek(0)
            r_task = TaskCofactors(
                reacfile=temp_reacfile.name, cmpdfile=self.compdfile_wo_cofactors, cofile=self.cofile
            )
            r_task.compute(timeout=None)
            # Check if the mocked methods were called
            mock_read_cofactors.assert_called_once()
            mock_rm_cofactors_in_cmpdfile.assert_called_once()
            mock_dict_from_reacfile.assert_called_once()
            mock_clean_reactions.assert_called_once()
            mock_parse_reacfile.assert_called_once()
            mock_merge_reactions_rules.assert_called_once()
            # Compare new reactions file with expected result
            self.assertEqual(
                open(temp_reacfile.name, 'r').read(),
                open(self.reacfile_wo_cofactors, 'r').read()
            )