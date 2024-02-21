
BUILD_DIR            ?=  build
ARCHIVING_DIR        :=  $(BUILD_DIR)/tmp
ZIP_FILE             ?=  $(BUILD_DIR)/docker-rate-limit.pyz
PYTHON_SHEBANG       ?= $(shell scripts/detect_python_interpreter.sh)
ADD_PYTHON_SHEBANG   ?= true

PYTHON_MODULE        ?=  docker_rate_limit
PYTHON_MODULE_FILES  := $(shell find $(PYTHON_MODULE) -type f -iname '*.py')
PYTHON_MODULE_DIRS   := $(shell find $(PYTHON_MODULE) -type d)

BUILD_PYTHON_MODULE_FILES  := $(subst $(PYTHON_MODULE),$(ARCHIVING_DIR)/$(PYTHON_MODULE),$(PYTHON_MODULE_FILES))
BUILD_PYTHON_MODULE_DIRS   := $(subst $(PYTHON_MODULE),$(ARCHIVING_DIR)/$(PYTHON_MODULE),$(PYTHON_MODULE_DIRS))

.PHONY: all clean zipfile

all:
	@echo "Available Targets:"
	@echo ""
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

zipfile: $(ZIP_FILE)

$(ZIP_FILE): $(BUILD_PYTHON_MODULE_FILES) | $(ARCHIVING_DIR) $(BUILD_PYTHON_MODULE_DIRS)
	@echo " [GEN]     $@"
ifeq ($(ADD_PYTHON_SHEBANG),false)
	@$(PYTHON_SHEBANG) -m zipapp \
		--compress \
		--main "$(PYTHON_MODULE).__main__:main" \
		--output "$@" \
		"$(ARCHIVING_DIR)"
else
	@$(PYTHON_SHEBANG) -m zipapp \
		--compress \
		--main "$(PYTHON_MODULE).__main__:main" \
		--output "$@" \
		--python "$(PYTHON_SHEBANG)" \
		"$(ARCHIVING_DIR)"
endif

$(ARCHIVING_DIR)/%.py: $(PYTHON_MODULE_FILES) | $(BUILD_PYTHON_MODULE_DIRS)
	@echo " [CP]      $(subst $(ARCHIVING_DIR)/,,$@) -> $@"
	@cp "$(subst $(ARCHIVING_DIR)/,,$@)" "$@"

$(BUILD_PYTHON_MODULE_DIRS): | $(ARCHIVING_DIR)
	@echo " [MK]      $@"
	@mkdir -p "$@"

$(ARCHIVING_DIR): | $(BUILD_DIR)
	@echo " [MK]      $@"
	@mkdir -p "$@"

$(BUILD_DIR):
	@echo " [MK]      $@"
	@mkdir -p "$@"

