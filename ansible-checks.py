#! /usr/bin/env python3
from subprocess import PIPE, Popen
import json
import yaml
import os
import logging
import argparse
import sys

# Parse command line arguments
parser = argparse.ArgumentParser(
    description='Check ansible playbook plays on several inventories')
parser.add_argument('--log', dest='loglevel', nargs="?")

args = parser.parse_args()

# Apply command line configuration
if args.loglevel is not None:
    numeric_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    logging.basicConfig(level=numeric_level)

# main
env = os.environ.copy()
env['ANSIBLE_STDOUT_CALLBACK'] = 'json'


with open("ansible-checks.yml", 'r') as stream:
    data = yaml.load(stream)

    for inventory in data:
        environment = inventory["environment"]
        playbooks = inventory["playbooks"]

        if not os.path.exists(environment):
            logging.error("Path doesn't exists: %s" % environment)
            sys.exit(2)

        for playbook in playbooks:
            if not os.path.exists(playbook):
                logging.error("Playbook doesn't exists: %s" % playbook)
                sys.exit(3)

            print("%s : %s" % (environment, playbook))
            command = [
                        "ansible-playbook", "-i", environment,
                        playbook, "--check",
                        # '--flush-cache', # Bug in Ansible 2.4.0
                    ]
            try:
                proc = Popen(
                    command,
                    env=env,
                    stdout=PIPE,
                    stderr=PIPE
                )
                json_output, _ = proc.communicate()
                logging.debug(json_output)
                status = json.loads(json_output.decode())["stats"]

                for host, values in status.items():
                    output = []
                    errors = values["unreachable"] + values["failures"]
                    changed = values["changed"]

                    if errors > 0:
                        output.append("errors: %s" % errors)

                    if changed > 0:
                        output.append("changes: %s" % changed)

                    if len(output) > 0:
                        print("    %s : %s" % (host, ", ".join(output)))

            except Exception as e: 
                print( "Error running command '%s'" % ' '.join(command))
                print( "%s : %s " % (type(e),e))
