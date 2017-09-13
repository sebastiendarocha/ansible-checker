#! /usr/bin/python3
from subprocess import PIPE, Popen
import json
import yaml
from pprint import pprint
import os

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
