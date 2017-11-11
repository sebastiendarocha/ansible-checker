#! /usr/bin/env python3

import unittest
import shutil
import os
import subprocess
import yaml
import utils

class TestAnsibleCheckYamlOutput(unittest.TestCase):
    def setup_method(self, method):
        try:
            os.remove("ansible-checks.yml")
        except OSError:
            pass
        utils.install_config_test_file(method.__name__)

    def testErrorConfAbsentYaml(self):
        try:
            os.remove("ansible-checks.yml")
        except OSError:
            pass

        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output('../ansible-checks.py',
                                    stderr=subprocess.STDOUT)

        self.assertTrue("returned non-zero exit status 1"
                        in str(context.exception))

    def testErrorInventoryYaml(self):

        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output('../ansible-checks.py',
                                    stderr=subprocess.STDOUT)

        self.assertIn("returned non-zero exit status 2",
                      str(context.exception))
        self.assertIn("Path doesn't exists: hosts_fail",
                      str(context.exception.output.decode()))

    def testErrorPlaybookYaml(self):

        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output('../ansible-checks.py',
                                    stderr=subprocess.STDOUT)

        self.assertIn("returned non-zero exit status 3",
                      str(context.exception))
        self.assertIn("Playbook doesn't exists: not_exists.yml",
                      str(context.exception.output))

    def testConfChangedPlaybookYaml(self):

        output = subprocess.check_output('../ansible-checks.py',
                                         stderr=subprocess.STDOUT)

        with open("expect_results/yaml_output_changed_playbook.yml") as f:
            self.assertEqual(f.read(), output.decode())

