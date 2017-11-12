#! /usr/bin/env python3

import unittest
import os
import subprocess
import utils


class TestAnsibleCheckYamlOutput(unittest.TestCase):
    def setup_method(self, method):
        try:
            os.remove("ansible-checks.yml")
        except OSError:
            pass

        utils.install_config_test_file(method.__name__)

        if "expected_result" in self.__dict__:
            del self.expected_result

        try:
            with open(utils.get_expected_test_file(method.__name__)) as f:
                self.expected_result = f.read()
        except OSError:
            pass

    def testErrorConfAbsentYaml(self):
        try:
            os.remove("ansible-checks.yml")
        except OSError:
            pass

        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output('../ansible_checks.py',
                                    stderr=subprocess.STDOUT)

        self.assertTrue("returned non-zero exit status 1"
                        in str(context.exception))

    def testErrorInventoryYaml(self):

        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output('../ansible_checks.py',
                                    stderr=subprocess.STDOUT)

        self.assertIn("returned non-zero exit status 2",
                      str(context.exception))
        self.assertIn("Path doesn't exists: hosts_fail",
                      str(context.exception.output.decode()))

    def testErrorPlaybookYaml(self):

        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output('../ansible_checks.py',
                                    stderr=subprocess.STDOUT)

        self.assertIn("returned non-zero exit status 3",
                      str(context.exception))
        self.assertIn("Playbook doesn't exists: not_exists.yml",
                      str(context.exception.output))

    def testConfChangedPlaybookYaml(self):

        output = subprocess.check_output('../ansible_checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual(self.expected_result, output.decode())

    def testConfSimplePlaybookYaml(self):

        output = subprocess.check_output('../ansible_checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual(self.expected_result, output.decode())

    def testConfErrorPlaybookYaml(self):

        output = subprocess.check_output('../ansible_checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual(self.expected_result, output.decode())

    def testConfTwoPlaybooksYaml(self):

        output = subprocess.check_output('../ansible_checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual(self.expected_result, output.decode())
