#! /usr/bin/env python3

import unittest
import os
import subprocess
import yaml

def createConf(config):
    """ Fill the yaml configuration file """
    with open('ansible-checks.yml', 'w') as yaml_file:
        yaml.dump(config, yaml_file, default_flow_style=False)


class TestAnsibleCheckRun(unittest.TestCase):
    def setUp(self):
        try:
            os.remove("ansible-checks.yml")
        except OSError:
            pass

    def testErrorConfAbsent(self):
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output('../ansible-checks.py',
                                    stderr=subprocess.STDOUT)

        self.assertTrue("returned non-zero exit status 1"
                        in str(context.exception))

    def testErrorInventory(self):
        conf = [
            dict(environment="hosts_fail",
                 playbooks=["changed.yml"])
        ]
        createConf(conf)

        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output('../ansible-checks.py',
                                    stderr=subprocess.STDOUT)

        self.assertIn("returned non-zero exit status 2",
                      str(context.exception))
        self.assertIn("Path doesn't exists: hosts_fail",
                      str(context.exception.output.decode()))

    def testErrorPlaybook(self):
        conf = [
            dict(environment="hosts",
                 playbooks=["not_exists.yml"])
        ]
        createConf(conf)

        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output('../ansible-checks.py',
                                    stderr=subprocess.STDOUT)

        self.assertIn("returned non-zero exit status 3",
                      str(context.exception))
        self.assertIn("Playbook doesn't exists: not_exists.yml",
                      str(context.exception.output))

    def testConfChandedPlaybook(self):
        conf = [
            dict(environment="hosts",
                 playbooks=["changed.yml"])
        ]
        createConf(conf)

        output = subprocess.check_output('../ansible-checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual("hosts : changed.yml\n"
                         "    localhost : changes: 1\n",
                         output.decode())

    def testConfSimplePlaybook(self):
        conf = [
            dict(environment="hosts",
                 playbooks=["simple.yml"])
        ]
        createConf(conf)

        output = subprocess.check_output('../ansible-checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual("hosts : simple.yml\n", output.decode())

    def testConfErrorPlaybook(self):
        conf = [
            dict(environment="hosts",
                 playbooks=["error.yml"])
        ]
        createConf(conf)

        output = subprocess.check_output('../ansible-checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual("hosts : error.yml\n"
                         "    localhost : errors: 1\n",
                         output.decode())

    def testConfTwoPlaybooks(self):
        conf = [
            dict(environment="hosts",
                 playbooks=[
                     "allinone.yml",
                     "simple.yml",
                 ])
        ]
        createConf(conf)

        output = subprocess.check_output('../ansible-checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual("hosts : allinone.yml\n"
                         "    localhost : errors: 1, changes: 1\n"
                         "hosts : simple.yml\n",
                         output.decode())

if __name__ == '__main__':
    unittest.main()
