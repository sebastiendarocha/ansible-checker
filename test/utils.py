import re
import yaml
import shutil

# https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def installConf(filename):
    shutil.copy(filename,"ansible-checks.yml")

def get_config_test_file(test):
    test_base = test[4:]
    return "configs/%s.yml" % to_snake_case(test_base)

def get_expected_test_file(test):
    test_base = test[4:]
    return "expect_results/%s.yml" % to_snake_case(test_base)

def install_config_test_file(method):
    installConf(get_config_test_file(method))

def createConf(config):
    """ Fill the yaml configuration file """
    with open('ansible-checks.yml', 'w') as yaml_file:
        yaml.dump(config, yaml_file, default_flow_style=False)

