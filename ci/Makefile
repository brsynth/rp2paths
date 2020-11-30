SELF_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

include $(SELF_DIR)/.env
include $(SELF_DIR)/../extras/.env

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help test

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

# cli args
ARGS = $(filter-out $@,$(MAKECMDGOALS))

MAKE_CMD = $(MAKE) -s --no-print-directory -C makefiles

# Default environment
ifeq ($(env),)
	env = ${PACKAGE}_build
endif

clean:
	@$(MAKE_CMD) -f conda.mk clean

# FAST TESTING
check: ## Test code with 'pytest', this is the fastest way to test the code
	   @$(MAKE_CMD) -f test.mk check

test: ## Test code with 'pytest', this is the fastest way to test the code
	   @$(MAKE_CMD) -f test.mk test args=$(args)

%-inconda: ## Test conda package
ifneq ($(strip $(env)),)
	$(eval env=${PACKAGE}_$*)
endif
	@$(MAKE_CMD) -f conda.mk check-environment-$* env=$(env)
	@$(MAKE_CMD) -f conda.mk conda-run-env env=$(env) \
																				 cmd="make -C .. $*" \
																				 args="$(args)"


conda-all: conda-build conda-test conda-convert conda-publish ## (default) Perform all conda process (build, test, convert, publish)

# CONDA WORKFLOW
conda-build: ## Build (without tests) conda package, 'variants=<variants>' option can be passed (format must be fully compliant with '--variants' option of conda-build)
	@$(MAKE_CMD) -f conda.mk conda-build-only env=$(env) variants="$(variants)"

conda-test: ## Test conda package
	@$(MAKE_CMD) -f conda.mk conda-test-only env=$(env)

conda-convert: ## Convert conda package towards all platforms, if 'python=<version>' (default is all variants of package built) is set then the package built for this version of Python will be converted
	@$(MAKE_CMD) -f conda.mk conda-convert env=$(env)

conda-publish: ## Publish conda package, if 'python=<version>' (default is all variants of package built) is set then the package built for this version of Python will be published
	@$(MAKE_CMD) -f conda.mk conda-publish env=$(env)

conda-check-recipe: ## Check conda recipe
	@$(MAKE_CMD) -f conda.mk conda-recipe-check

conda-create-run_env: ## Make an conda environment to run program
	@$(MAKE_CMD) -f conda.mk check-environment-test env=${PACKAGE}_test
