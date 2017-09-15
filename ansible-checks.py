#! /usr/bin/python3
from subprocess import PIPE, Popen
import json
import yaml
import os
import logging
import argparse

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

        for playbook in playbooks:
            print("%s : %s" % (environment, playbook))
            proc = Popen(
                [
                    "ansible-playbook", "-i", environment,
                    playbook, '--flush-cache', "--check"
                ],
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
