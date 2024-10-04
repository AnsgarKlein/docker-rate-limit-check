
.POSIX:

LINT_SCRIPT          ?=  scripts/lint.sh

BUILD_DIR            ?=  build
ZIP_FILE             ?=  $(BUILD_DIR)/docker-rate-limit.pyz
PYTHON_SHEBANG       ?=  $(shell scripts/detect_python_interpreter.sh)
ADD_PYTHON_SHEBANG   ?=  true

PYTHON_MODULE        ?=  docker_rate_limit_check
PYTHON_MODULE_FILES  :=  $(shell find $(PYTHON_MODULE) -type f -iname '*.py')
PYTHON_MODULE_DIRS   :=  $(shell find $(PYTHON_MODULE) -type d -not -name '__pycache__')

ZIPFILE_DIR                  := $(BUILD_DIR)/zipappbuild
ZIPFILE_LAUNCHER             := $(ZIPFILE_DIR)/__main__.py
ZIPFILE_PYTHON_MODULE        := $(ZIPFILE_DIR)/$(PYTHON_MODULE)
ZIPFILE_PYTHON_MODULE_FILES  := $(foreach file, $(PYTHON_MODULE_FILES),$(shell echo "$(ZIPFILE_DIR)/$(file)"))
ZIPFILE_PYTHON_MODULE_DIRS   := $(foreach dir, $(PYTHON_MODULE_DIRS),$(shell echo "$(ZIPFILE_DIR)/$(dir)"))

PYPROJECT_FILE       := pyproject.toml
REQUIREMENTS_FILE    := requirements.txt
REQUIREMENTS_DEV_FILE := requirements-dev.txt


.PHONY: all
all:
	@echo "Available Targets:"
	@echo ""
	@echo "  - lint"
	@echo "      Lint project"
	@echo "  - update-requirements"
	@echo "      Use pip-tools to update the package versions specified in the"
	@echo "      requirement files to the latest supported version."
	@echo "  - zipfile"
	@echo "      Pack all python files of this project into a single .pyz"
	@echo "      Python archive file that can be executed using a python"
	@echo "      interpreter or executed directly using Shebang value."
	@echo ""
	@echo "      Environment variables:"
	@echo "        * ADD_PYTHON_SHEBANG"
	@echo "          Whether to add the python interpreter as Shebang"
	@echo "          to resulting Python archive."
	@echo "          Default: true"
	@echo "          Currently: $(ADD_PYTHON_SHEBANG)"
	@echo "        * PYTHON_SHEBANG"
	@echo "          Python interpreter to include in Python archive as"
	@echo "          Shebang."
	@echo "          Will be automatically detected by default."
	@echo "          Currently: $(PYTHON_SHEBANG)"

.PHONY: clean
clean:
	@echo " [RM]      $(ZIP_FILE)"
	@rm -f "$(ZIP_FILE)"
	@echo " [RM]      $(ZIPFILE_LAUNCHER)"
	@rm -f "$(ZIPFILE_LAUNCHER)"
	@# TODO: 
	@echo " TODO: Delete build directory"

.PHONY: lint
lint:
	@$(LINT_SCRIPT)


##
## Build directory
##

$(BUILD_DIR):
	@echo " [MK]      $@"
	@mkdir -p "$@"


##
## ZIP file
##

.PHONY: zipfile
zipfile: $(ZIP_FILE)

$(ZIP_FILE): $(ZIPFILE_LAUNCHER) $(ZIPFILE_PYTHON_MODULE_FILES) | $(ZIPFILE_PYTHON_MODULE_DIRS)
	@echo " [GEN]     $@"
ifeq ($(ADD_PYTHON_SHEBANG),false)
	@$(PYTHON_SHEBANG) -m zipapp \
		--compress \
		--output "$@" \
		$(ZIPFILE_DIR)
else
	@$(PYTHON_SHEBANG) -m zipapp \
		--compress \
		--output "$@" \
		--python "$(PYTHON_SHEBANG)" \
		$(ZIPFILE_DIR)
endif

$(ZIPFILE_LAUNCHER): | $(ZIPFILE_DIR)
	@echo " [GEN]     $@"
	@echo 'from $(PYTHON_MODULE).__main__ import main\n\nmain()' > $@

$(ZIPFILE_PYTHON_MODULE)/%.py: $(PYTHON_MODULE_FILES) | $(ZIPFILE_PYTHON_MODULE_DIRS)
	@echo " [CP]      $(subst $(ZIPFILE_PYTHON_MODULE)/,$(PYTHON_MODULE)/,$@) -> $@"
	@cp "$(subst $(ZIPFILE_PYTHON_MODULE)/,$(PYTHON_MODULE)/,$@)" "$@"

$(ZIPFILE_PYTHON_MODULE_DIRS): | $(ZIPFILE_DIR)
	@echo " [MK]      $@"
	@mkdir -p "$@"

$(ZIPFILE_DIR): | $(BUILD_DIR)
	@echo " [MK]      $@"
	@mkdir -p "$@"


##
## Requirements files
##

.PHONY: update-requirements
update-requirements: $(REQUIREMENTS_FILE) $(REQUIREMENTS_DEV_FILE)

.PHONY: $(REQUIREMENTS_FILE)
$(REQUIREMENTS_FILE): $(PYPROJECT_FILE)
ifeq ("$(VIRTUAL_ENV)","")
	@echo "Error: No virtualenv activated" > /dev/stderr
	@echo "Activate virtualenv first" > /dev/stderr
	@exit 1
else
	@echo " [GEN]     $^ -> $@"
	@pip-compile --upgrade --quiet --allow-unsafe -o "$@"
endif

.PHONY: $(REQUIREMENTS_DEV_FILE)
$(REQUIREMENTS_DEV_FILE): $(PYPROJECT_FILE)
ifeq ("$(VIRTUAL_ENV)","")
	@echo "Error: No virtualenv activated" > /dev/stderr
	@echo "Activate virtualenv first" > /dev/stderr
	@exit 1
else
	@echo " [GEN]     $^ -> $@"
	@pip-compile --upgrade --quiet --allow-unsafe --extra dev -o "$@"
endif
