
LINT_SCRIPT          ?=  scripts/lint.sh

BUILD_DIR            ?=  build
ZIP_FILE             ?=  $(BUILD_DIR)/docker-rate-limit.pyz
PYTHON_SHEBANG       ?=  $(shell scripts/detect_python_interpreter.sh)
ADD_PYTHON_SHEBANG   ?=  true

PYTHON_MODULE        ?=  docker_rate_limit
PYTHON_MODULE_FILES  :=  $(shell find $(PYTHON_MODULE) -type f -iname '*.py')
PYTHON_MODULE_DIRS   :=  $(shell find $(PYTHON_MODULE) -type d -not -name '__pycache__')

BUILD_PYTHON_MODULE        := $(BUILD_DIR)/$(PYTHON_MODULE)
BUILD_PYTHON_MODULE_FILES  := $(foreach file, $(PYTHON_MODULE_FILES),$(shell echo "$(BUILD_DIR)/$(file)"))
BUILD_PYTHON_MODULE_DIRS   := $(foreach dir, $(PYTHON_MODULE_DIRS),$(shell echo "$(BUILD_DIR)/$(dir)"))

ZIPFILE_LAUNCHER     := $(BUILD_DIR)/$(PYTHON_MODULE)-zipfile_launcher.py

.PHONY: all clean lint zipfile

all:
	@echo "Available Targets:"
	@echo ""
	@echo "  - lint"
	@echo "      Lint project"
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

clean:
	@echo " [RM]      $(ZIP_FILE)"
	@rm -f "$(ZIP_FILE)"
	@# TODO: 
	@echo " TODO: Delete build directory"

lint:
	@$(LINT_SCRIPT)

zipfile: $(ZIP_FILE)

$(ZIP_FILE): $(ZIPFILE_LAUNCHER) $(BUILD_PYTHON_MODULE_FILES) | $(BUILD_PYTHON_MODULE_DIRS)
	@echo " [GEN]     $@"
ifeq ($(ADD_PYTHON_SHEBANG),false)
	@$(PYTHON_SHEBANG) -m zipapp \
		--compress \
		--output "$@" \
		$(ZIPFILE_LAUNCHER)
else
	@$(PYTHON_SHEBANG) -m zipapp \
		--compress \
		--output "$@" \
		--python "$(PYTHON_SHEBANG)" \
		$(ZIPFILE_LAUNCHER)
endif

.INTERMEDIATE: $(ZIPFILE_LAUNCHER)
$(ZIPFILE_LAUNCHER): | $(BUILD_DIR)
	@echo " [GEN]     $@"
	@echo 'from $(PYTHON_MODULE).__main__ import main\n\nmain()' > $@

$(BUILD_PYTHON_MODULE)/%.py: $(PYTHON_MODULE_FILES) | $(BUILD_PYTHON_MODULE_DIRS)
	@echo " [CP]      $(subst $(BUILD_PYTHON_MODULE)/,$(PYTHON_MODULE)/,$@) -> $@"
	@cp "$(subst $(BUILD_PYTHON_MODULE)/,$(PYTHON_MODULE)/,$@)" "$@"

$(BUILD_PYTHON_MODULE_DIRS):
	@echo " [MK]      $@"
	@mkdir -p "$@"

$(BUILD_DIR):
	@echo " [MK]      $@"
	@mkdir -p "$@"

