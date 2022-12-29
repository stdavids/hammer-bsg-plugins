#!/usr/bin/env python3
import argparse
import json
import os
import sys
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("--env", required=True)
parser.add_argument("--dir", required=True)
parser.add_argument("--dve", action="store_true")
parser.add_argument("--type", required="--dve" not in sys.argv, choices=["rtl", "rtl-hard", "syn", "syn-functional", "par", "par-functional"])
parser.add_argument("--cfg", required="--dve" not in sys.argv)
args = parser.parse_args()

flags = []
env = {}
cfg = {}

with open(args.env, "r") as f:
    env = yaml.safe_load(f)

if not args.dve:
    with open(args.cfg, "r") as f:
        cfg = json.load(f)

### DVE ###
if args.dve:
    ### Environment variables ###
    flags += [f"export SNPSLMD_LICENSE_FILE={env['synopsys.SNPSLMD_LICENSE_FILE']};"]
    flags += [f"export VCS_HOME={os.sep.join([env['synopsys.synopsys_home'],'vcs',env['sim.vcs.version']])};"]
    ### DVE binary ###
    flags += [f"{os.sep.join([env['synopsys.synopsys_home'],'vcs',env['sim.vcs.version']])}/bin/dve"]
    ### Common flags ###
    flags += ["-full64", "-vpd", os.sep.join([args.dir, "vcdplus.vpd"])]

### VCS ###
else:
    ### Environment variables ###
    flags += [f"export SNPSLMD_LICENSE_FILE={env['synopsys.SNPSLMD_LICENSE_FILE']};"]
    flags += [f"export VCS_HOME={os.sep.join([env['synopsys.synopsys_home'],'vcs',env['sim.vcs.version']])};"]
    # VCS binary ###
    flags += [f"{os.sep.join([env['synopsys.synopsys_home'],'vcs',env['sim.vcs.version']])}/bin/vcs"]
    ### Common flags ###
    flags += ["-full64", "-override_timescale=1ps/1ps", "-sverilog", f"-Mdir={args.dir}", f"-o {os.sep.join([args.dir, 'simv'])}"]
    ### Debug + waveform ###
    flags += ["-debug_access+all"]
    ### Design input ###
    flags += ["-top", cfg["sim.inputs.tb_name"]]
    flags += cfg["sim.inputs.input_files"]
    flags += cfg["sim.inputs.tb_input_files"]
    if "sim.inputs.tb_incdir" in cfg:
        flags += ["+incdir+" + i for i in cfg["sim.inputs.tb_incdir"]]
    ### RTL SPECIFIC FLAGS ###
    if args.type == "rtl":
        pass
    ### RTL HARD SPECIFIC FLAGS ###
    elif args.type == "rtl-hard":
        pass
    ### SYN FUNCTIONAL SPECIFIC FLAGS ###
    elif args.type == "syn-functional":
        pass
    ### SYN SPECIFIC FLAGS ###
    elif args.type == "syn":
        flags += ["build/tech-sky130-cache/primitives.v", "build/tech-sky130-cache/sky130_fd_sc_hd.v"]
        flags += ["-sdf", f"max:{cfg['sim.inputs.top_module']}:{cfg['sim.inputs.sdf_file']}"]
        flags += ["+neg_tchk", "+sdfverbose", "-negdelay"]
        flags += ["+define+FUNCTIONAL", "+define+UNIT_DELAY"]
        flags += ["+warn=noSDFCOM_UHICD", "+warn=noSDFCOM_ANICD"]
    ### PAR FUNCTIONAL SPECIFIC FLAGS ###
    elif args.type == "par-functional":
        pass
    ### PAR SPECIFIC FLAGS ###
    elif args.type == "par":
        flags += ["build/tech-sky130-cache/primitives.v", "build/tech-sky130-cache/sky130_fd_sc_hd.v"]
        flags += ["-sdf", f"max:{cfg['sim.inputs.top_module']}:{cfg['sim.inputs.sdf_file']}"]
        flags += ["+neg_tchk", "+sdfverbose", "-negdelay"]
        flags += ["+define+FUNCTIONAL", "+define+UNIT_DELAY"]
        flags += ["+warn=noSDFCOM_UHICD", "+warn=noSDFCOM_ANICD"]

### Print out the command ###
print(" ".join(flags))
sys.exit(0)

