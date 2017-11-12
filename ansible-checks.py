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

result = {}

with open("ansible-checks.yml", 'r') as stream:
    data = yaml.load(stream)
    output_format = data.get("output", None)
    environments = data.get("environments", [])

    for inventory in environments:
        environment = inventory["environment"]
        playbooks = inventory["playbooks"]

        result_environments = result.setdefault('environments', [])
        result_environment = dict(name=environment)

        result_playbooks = result_environment.setdefault('playbooks', [])
        if not os.path.exists(environment):
            logging.error("Path doesn't exists: %s" % environment)
            sys.exit(2)

        for playbook in playbooks:
            if not os.path.exists(playbook):
                logging.error("Playbook doesn't exists: %s" % playbook)
                sys.exit(3)

            result_playbook = dict(name=playbook)
            result_playbooks.append(result_playbook)
            result_hosts = result_playbook.setdefault('hosts', [])

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

                    logging.debug(values)

                    errors = values["unreachable"] + values["failures"]
                    changed = values["changed"]
                    success = values["ok"]

                    result_host = dict(name=host)

                    result_host['errors'] = errors
                    result_host['changes'] = changed
# TODO Something wrong
                    result_host['success'] = changed

                    result_hosts.append(result_host)

            except Exception as e:
                print("Error running command '%s'" % ' '.join(command))
                print("%s : %s " % (type(e), e))

        result_environments.append(result_environment)

    if output_format == "yaml":

        print(yaml.dump(result, default_flow_style=False))

    elif output_format is None:

        for environment in result.get("environments", []):
            for playbook in environment['playbooks']:
                print("%s : %s" % (environment['name'], playbook['name']))

                for host in playbook['hosts']:
                    output = []

                    if host["errors"] > 0:
                        output.append("errors: %s" % host["errors"])

                    if host['changes'] > 0:
                        output.append("changes: %s" % host["changes"])

                    if len(output) > 0:
                        print("    %s : %s" %
                              (host['name'], ", ".join(output)))
