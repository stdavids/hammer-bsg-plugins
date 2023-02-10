# This one line causes errors elsewhere...
#THIS_DIR := $(realpath $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST)))))

REAL_OBJ_DIR = $(realpath $(OBJ_DIR))

RUBYLIB := /home/projects/ee477.2023wtr/cad/klayout/ruby/lib64/ruby
RUBYLIB := $(RUBYLIB):/home/projects/ee477.2023wtr/cad/klayout/ruby/lib64/rubygems
RUBYLIB := $(RUBYLIB):/home/projects/ee477.2023wtr/cad/klayout/ruby/share/ruby

KLAYOUT := RUBYLIB=$(RUBYLIB) /home/projects/ee477.2023wtr/cad/klayout/klayout
KLAYOUT_GDS_FILE := $(firstword $(wildcard $(REAL_OBJ_DIR)/par-rundir/*.gds/))

# TODO: un hard code? Make hook?
open-klayout-gds:
	$(KLAYOUT) -l /home/projects/ee477/cad/pdk/sky130A/libs.tech/klayout/sky130A.lyp $(KLAYOUT_GDS_FILE)
	

