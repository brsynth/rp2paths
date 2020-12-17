# Release history

## 1.4.2
- ci: integrate CI toolkit
- chore: switch to openjdk dependency

## 1.4.1
- build: provide conda packaging
- build: remove pip packaging
- ci(publish): add github workflows for testing build and publishing 
- docs(readme): update
- fix(setup.py): remove requirements file for unit tests

## 1.4.0
- feat: rp2paths is now packaged!
- fix: set maxstep argument default value to +inf (instead of 15)
- style: improve PEP style, correct typos
- docs: add "installation for developers" section
- tests: refactor test scripts

## 1.3.3
- Add an exception to handle the case when no scope matrix is produced
- Add a test with an input that produces no scope matrix

## 1.3.2
- In Docker environment, switch to Debian based image (brsynth/rdkit:debian)

## 1.3.1
- In Docker environment, specify base image tag (brsynth/rdkit:alpine)

## 1.3.0
- Add source into the docker image
- Rename tests scripts

## 1.2.0
- Add docker folder
- Add tests for standalone and docker modes

## 1.1.0
- Add Dockerfile
- Add test folder

## 1.0.2
- Add #!/ she-bang to make `*.py` executable

## 1.0.1
- Documentation update
- Update code to please numpy
- Improve handling of rules and compounds IDs in dot files
- Change default path the compounds-name file
- Fix name rendering in output files
