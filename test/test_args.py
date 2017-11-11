#! /usr/bin/env python3

import unittest
import os
import subprocess
import utils


class TestAnsibleCheckArgs(unittest.TestCase):
    """ test the command line interface """

    def setUp(self):
        conf = dict(
            environment= []
        )
        utils.createConf(conf)

    def testNoArguments(self):
        output = subprocess.check_output('../ansible-checks.py',
                                         stderr=subprocess.STDOUT)

        self.assertEqual("", output.decode())

    def testHelpArguments(self):
        output = subprocess.check_output(
            [
                '../ansible-checks.py',
                '-h'
            ],
            stderr=subprocess.STDOUT)

        self.assertIn("Check ansible playbook plays on several inventories",
                      output.decode())

    def testLoglevelArguments(self):
        output = subprocess.check_output(
            [
                '../ansible-checks.py',
                '--log',
                'DEBUG'
            ],
            stderr=subprocess.STDOUT)

        self.assertEqual("", output.decode())

    def testWrongLoglevelArgument(self):
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output(
                [
                    '../ansible-checks.py',
                    '--log',
                    'DEBUGFAIL'
                ],
                stderr=subprocess.STDOUT)

        self.assertIn("Invalid log level: ", str(context.exception.output))
