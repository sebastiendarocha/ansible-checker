#! /usr/bin/env python3
"""
Check ansible playbook plays on several inventories
"""

from subprocess import PIPE, Popen, CalledProcessError
import argparse
import json
import logging
import os
import sys
import yaml


def _parse_host(host, values):
    """
    return a dictionnary containing the host name, the errors, changes
    and success
    """
    logging.debug(values)

    errors = values["unreachable"] + values["failures"]
    changed = values["changed"]
    success = values["ok"]

    result_host = dict(name=host)

    result_host['errors'] = errors
    result_host['changes'] = changed
    result_host['success'] = success
    return result_host


def _parse_and_run_playbook(environment, playbook, env):
    if not os.path.exists(playbook):
        logging.error("Playbook doesn't exists: %s", playbook)
        sys.exit(3)

    result_playbook = dict(name=playbook)
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
            result_hosts.append(_parse_host(host, values))

    except ValueError as ex:
        print("Error parsing output command '%s'"
              % ' '.join(command))
        print("%s : %s " % (type(ex), ex))

    except CalledProcessError as ex:
        print("Error running command '%s'" % ' '.join(command))
        print("%s : %s " % (type(ex), ex))

    return result_playbook


def _print_human_result(result):
    for environment in result.get("environments", []):
        for playbook in environment['playbooks']:
            print("%s : %s" % (environment['name'], playbook['name']))

            for host in playbook['hosts']:
                output = []

                if host["errors"] > 0:
                    output.append("errors: %s" % host["errors"])

                if host['changes'] > 0:
                    output.append("changes: %s" % host["changes"])

                if output:
                    print("    %s : %s" %
                          (host['name'], ", ".join(output)))


def main():
    """
    Calls all playbook in their environments and print the summary in yaml
    or human format
    """

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
                logging.error("Path doesn't exists: %s", environment)
                sys.exit(2)

            for playbook in playbooks:
                result_playbooks.append(
                    _parse_and_run_playbook(environment, playbook, env)
                )

            result_environments.append(result_environment)

        if output_format == "yaml":
            print(yaml.dump(result, default_flow_style=False))

        elif output_format is None:
            _print_human_result(result)


def _parse_command_line_args():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=__doc__)
    parser.add_argument('--log', dest='loglevel', nargs="?")

    args = parser.parse_args()

    # Apply command line configuration
    if args.loglevel is not None:
        numeric_level = getattr(logging, args.loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % args.loglevel)
        logging.basicConfig(level=numeric_level)

if __name__ == "__main__":
    _parse_command_line_args()
    main()
