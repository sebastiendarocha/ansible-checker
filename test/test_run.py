#! /usr/bin/env python3

import unittest
import os
import subprocess
import utils


class TestAnsibleCheckRun(unittest.TestCase):
    def setup_method(self, method):
        try:
            os.remove("ansible-checks.yml")
        except OSError:
            pass
        utils.install_config_test_file(method.__name__)

    def testErrorConfAbsent(self):
        try:
            os.remove("ansible-checks.yml")
        except OSError:
            pass

        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output('../ansible-checks.py',
                                    stderr=subprocess.STDOUT)

        self.assertTrue("returned non-zero exit status 1"
                        in str(context.exception))

    def testErrorInventory(self):

        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output('../ansible-checks.py',
                                    stderr=subprocess.STDOUT)

        self.assertIn("returned non-zero exit status 2",
                      str(context.exception))
        self.assertIn("Path doesn't exists: hosts_fail",
                      str(context.exception.output.decode()))

    def testErrorPlaybook(self):

        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output('../ansible-checks.py',
                                    stderr=subprocess.STDOUT)

        self.assertIn("returned non-zero exit status 3",
                      str(context.exception))
        self.assertIn("Playbook doesn't exists: not_exists.yml",
                      str(context.exception.output))

    def testConfChandedPlaybook(self):

        output = subprocess.check_output('../ansible-checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual("hosts : changed.yml\n"
                         "    localhost : changes: 1\n",
                         output.decode())

    def testConfSimplePlaybook(self):

        output = subprocess.check_output('../ansible-checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual("hosts : simple.yml\n", output.decode())

    def testConfErrorPlaybook(self):

        output = subprocess.check_output('../ansible-checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual("hosts : error.yml\n"
                         "    localhost : errors: 1\n",
                         output.decode())

    def testConfTwoPlaybooks(self):

        output = subprocess.check_output('../ansible-checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual("hosts : allinone.yml\n"
                         "    localhost : errors: 1, changes: 1\n"
                         "hosts : simple.yml\n",
                         output.decode())
