from yaml     import safe_load as yaml_safe_load
from yaml     import YAMLError
from os       import path      as os_path
from shutil   import copyfile
from tempfile import NamedTemporaryFile
from sys      import argv as sys_argv

current_folder = os_path.dirname(os_path.realpath(__file__))

# input files
channels_file = current_folder+'/../../recipe/conda_channels.txt'
recipe_file   = current_folder+'/../../recipe/meta.yaml'
bld_cfg_file  = current_folder+'/../../recipe/conda_build_config.yaml'

def parse_meta(filename):

    recipe = ''
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            # filter all non-YAML elements
            if not line.startswith('{%') and '{{' not in line:
                recipe += line
            line = f.readline()

    requirements = []
    tests = {}
    try:
        try: requirements += yaml_safe_load(recipe)['requirements']['host']
        except TypeError: pass
        try: requirements += yaml_safe_load(recipe)['requirements']['run']
        except TypeError: pass
        try: requirements += yaml_safe_load(recipe)['test']['requires']
        except TypeError: pass
        tests['commands']     = yaml_safe_load(recipe)['test']['commands']
        tests['source_files'] = yaml_safe_load(recipe)['test']['source_files']
    except YAMLError as exc:
        print(exc)

    return requirements, tests




if __name__ == '__main__':

    requirements, tests = parse_meta(recipe_file)

    if any(arg in sys_argv for arg in ['test']):
        if len(sys_argv) < 3:
            args = 'commands sources'
        else:
            args = sys_argv
        if any(arg in args for arg in ['commands', 'cmd']):
            print(' && '.join(tests['commands']), end=' ')
        if any(arg in args for arg in ['sources', 'src']):
            print(' '.join(['../'+e for e in tests['source_files']]))
        else:
            print()

    if any(arg in sys_argv for arg in ['requirements', 'req']):
        print('channels:')
        print('\n'.join(['  - '+c for c in open(channels_file, 'r').read().split()]))
        print('dependencies:')
        print('\n'.join(['  - '+c for c in requirements]))
        print('  - pyyaml')
        exit()

        print(' '.join(['-c '+c for c in open(channels_file, 'r').read().split()]))
        if len(sys_argv) < 3:
            args = 'channels packages'
        else:
            args = sys_argv
        if any(arg in args for arg in ['channels']):
            print(' '.join(['-c '+c for c in open(channels_file, 'r').read().split()]), end=' ')
        if any(arg in args for arg in ['packages', 'pkg']):
            print(' '.join(requirements))
        else:
            print()
