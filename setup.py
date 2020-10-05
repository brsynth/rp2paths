from setuptools import setup
from re         import search as re_search

_readme_file  = 'README.md'
_release_file = 'RELEASE.md'
_extras_path  = 'extras'
_tests_path   = 'tests/pytest'

with open(_readme_file, 'r') as f:
    long_description = f.read()
with open(_release_file, 'r') as f:
    line = f.readline()
    while line:
        match = re_search("^## (\d\.\d\.\d)$", line)
        if match:
            _version = match.group(1)
            break
        line = f.readline()

with open(_extras_path+'/.env', 'r') as f:
    for line in f:
        if line.startswith('PACKAGE='):
            _package     = line.splitlines()[0].split('=')[1].lower()
        if line.startswith('URL='):
            _url         = line.splitlines()[0].split('=')[1].lower()
        if line.startswith('AUTHORS='):
            _authors     = line.splitlines()[0].split('=')[1].lower()
        if line.startswith('DESCR='):
            _descr       = line.splitlines()[0].split('=')[1].lower()
        if line.startswith('CORR_AUTHOR='):
            _corr_author = line.splitlines()[0].split('=')[1].lower()

required = []
with open(_extras_path+'/requirements.txt', 'r') as f:
    required = [line.splitlines()[0] for line in f]
tests_require = []
with open(_tests_path+'/requirements.txt', 'r') as f:
    tests_require = [line.splitlines()[0] for line in f]

# # hack to handle diff between pip and conda package name
# from sys import argv as sys_argv
# if 'conda' in sys_argv:
#     required += ['rdkit']

setup(
    name                          = _package,
    version                       = _version,
    author                        = _authors,
    author_email                  = _corr_author,
    description                   = _descr,
    long_description              = long_description,
    long_description_content_type = 'text/markdown',
    url                           = _url,
    packages                      = [_package],
    package_dir                   = {_package: 'rp2paths'},
    include_package_data          = True,
    install_requires              = required,
    test_suite                    = 'pytest',
    license                       = 'MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires               = '>=3.5',
)
