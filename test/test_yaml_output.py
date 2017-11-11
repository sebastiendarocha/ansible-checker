#! /usr/bin/env python3

import unittest
import shutil
import os
import subprocess
import yaml

def createConf(config):
    """ Fill the yaml configuration file """
    with open('ansible-checks.yml', 'w') as yaml_file:
        yaml.dump(config, yaml_file, default_flow_style=False)

def installConf(filename):
    shutil.copy(filename,"ansible-checks.yml")


class TestAnsibleCheckYamlOutput(unittest.TestCase):
    def setUp(self):
        try:
            os.remove("ansible-checks.yml")
        except OSError:
            pass

    def testConfChandedPlaybook(self):
        installConf("configs/changed_playbook.yml")

        output = subprocess.check_output('../ansible-checks.py',
                                         stderr=subprocess.STDOUT)

        with open("expect_results/yaml_output_changed_playbook.yml") as f:
            self.assertEqual(f.read(), output.decode())

