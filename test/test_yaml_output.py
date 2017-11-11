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

    def testConfChangedPlaybookYaml(self):

        output = subprocess.check_output('../ansible-checks.py',
                                         stderr=subprocess.STDOUT)

        with open("expect_results/yaml_output_changed_playbook.yml") as f:
            self.assertEqual(f.read(), output.decode())

