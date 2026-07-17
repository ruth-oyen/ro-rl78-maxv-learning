# This Makefile is intended to run from Git Bash.
SHELL := bash

# e2 studio workspace containing the PCJ and MCJ projects.
E2STUDIO_ROOT := ../../6_e2studio

# MCU-controlled JTAG firmware (MCJ).
MCJ := RO_RL78_MAXV_LEARNING_FW_MCJ
MCJ_PROJECT := $(E2STUDIO_ROOT)/$(MCJ)
MCJ_OUTPUT := fw/mcj
MCJ_SRC := $(MCJ_PROJECT)/src
MCJ_MOT := $(MCJ_PROJECT)/HardwareDebug/$(MCJ).mot
MCJ_ARCHIVE := $(MCJ_OUTPUT)/$(MCJ).tar.gz
MCJ_SRC_FILES := $(wildcard $(MCJ_SRC)/*)

# PC-controlled JTAG firmware (PCJ).
PCJ := RO_RL78_MAXV_LEARNING_FW_PCJ
PCJ_PROJECT := $(E2STUDIO_ROOT)/$(PCJ)
PCJ_OUTPUT := fw/pcj
PCJ_SRC := $(PCJ_PROJECT)/src
PCJ_MOT := $(PCJ_PROJECT)/HardwareDebug/$(PCJ).mot
PCJ_MOT_OUTPUT := $(PCJ_OUTPUT)/RO_RL78_MAXV_LEARNING_FW.mot
PCJ_ARCHIVE := $(PCJ_OUTPUT)/$(PCJ).tar.gz
PCJ_SRC_FILES := $(wildcard $(PCJ_SRC)/*)

# Copy changed firmware outputs into the repository.
.PHONY: fw_update clean
fw_update: $(MCJ_ARCHIVE) $(MCJ_OUTPUT)/$(MCJ).mot $(MCJ_OUTPUT)/src \
	   $(PCJ_ARCHIVE) $(PCJ_MOT_OUTPUT) $(PCJ_OUTPUT)/src

# Remove only the files and directories produced by fw_update.
clean:
	rm -rf "$(MCJ_ARCHIVE)" "$(MCJ_OUTPUT)/$(MCJ).mot" "$(MCJ_OUTPUT)/src" \
	       "$(PCJ_ARCHIVE)" "$(PCJ_MOT_OUTPUT)" "$(PCJ_OUTPUT)/src"

$(MCJ_OUTPUT) $(PCJ_OUTPUT):
	mkdir -p "$@"

# Store the complete e2 studio project for reproducible builds.
$(MCJ_ARCHIVE): $(MCJ_SRC_FILES) $(MCJ_MOT) $(MCJ_PROJECT) | $(MCJ_OUTPUT)
	tar --force-local -czf "$@" -C "$(E2STUDIO_ROOT)" "$(MCJ)"

$(MCJ_OUTPUT)/$(MCJ).mot: $(MCJ_MOT) | $(MCJ_OUTPUT)
	cp -f "$<" "$@"

$(MCJ_OUTPUT)/src: $(MCJ_SRC_FILES) $(MCJ_SRC) | $(MCJ_OUTPUT)
	rm -rf "$@"
	cp -a "$(MCJ_SRC)" "$@"
	touch "$@"

$(PCJ_ARCHIVE): $(PCJ_SRC_FILES) $(PCJ_MOT) $(PCJ_PROJECT) | $(PCJ_OUTPUT)
	tar --force-local -czf "$@" -C "$(E2STUDIO_ROOT)" "$(PCJ)"

# Keep the MOT and source tree outside the archive for readable Git diffs.
$(PCJ_MOT_OUTPUT): $(PCJ_MOT) | $(PCJ_OUTPUT)
	cp -f "$<" "$@"

$(PCJ_OUTPUT)/src: $(PCJ_SRC_FILES) $(PCJ_SRC) | $(PCJ_OUTPUT)
	rm -rf "$@"
	cp -a "$(PCJ_SRC)" "$@"
	touch "$@"
