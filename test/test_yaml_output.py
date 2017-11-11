#! /usr/bin/env python3

import unittest
import os
import subprocess
import yaml

def createConf(config):
    """ Fill the yaml configuration file """
    with open('ansible-checks.yml', 'w') as yaml_file:
        yaml.dump(config, yaml_file, default_flow_style=False)


class TestAnsibleCheckYamlOutput(unittest.TestCase):
    def setUp(self):
        try:
            os.remove("ansible-checks.yml")
        except OSError:
            pass

    def testConfChandedPlaybook(self):
        conf = dict(
            output='yaml',
            environments=
            [
                dict(
                    environment="hosts",
                    playbooks=["changed.yml"],
                    )
            ]
        )

        createConf(conf)

        output = subprocess.check_output('../ansible-checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual(
            "environments:\n"
            "- name: hosts\n"
            "  playbooks:\n"
            "  - hosts:\n"
            "    - changes: 1\n"
            "      errors: 0\n"
            "      name: localhost\n"
            "      success: 1\n"
            "    name: changed.yml\n"
            "\n",
            output.decode())

