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

    if "bsg_root" in cfg:
        sys.path.append(os.path.join(cfg["bsg_root"], "bsg_mem"))
        from bsg_ascii_to_rom import bsg_ascii_to_rom

### DVE ###
if args.dve:
    ### Environment variables ###
    flags += [f"export SNPSLMD_LICENSE_FILE={env['synopsys.SNPSLMD_LICENSE_FILE']};"]
    flags += [f"export VCS_HOME={os.path.join(env['synopsys.synopsys_home'],'vcs',env['sim.vcs.version'])};"]
    ### DVE binary ###
    flags += [f"{os.path.join(env['synopsys.synopsys_home'],'vcs',env['sim.vcs.version'])}/bin/dve"]
    ### Common flags ###
    flags += ["-full64", "-vpd", os.path.join(args.dir, "vcdplus.vpd")]

### VCS ###
else:
    ### Generate Trace Roms ###
    if "sim.inputs.trace_files" in cfg:
        for tr in cfg["sim.inputs.trace_files"]:
            module_name = os.path.splitext(os.path.basename(tr))[0] + "_rom"
            out_v_file = os.path.join(args.dir, module_name + ".v")
            with open(out_v_file, "w") as  f:
                bsg_ascii_to_rom(filename=tr, modulename=module_name, zero=0, spool=f)
            cfg["sim.inputs.tb_input_files"].append(out_v_file)
    ### Environment variables ###
    flags += [f"export SNPSLMD_LICENSE_FILE={env['synopsys.SNPSLMD_LICENSE_FILE']};"]
    flags += [f"export VCS_HOME={os.path.join(env['synopsys.synopsys_home'],'vcs',env['sim.vcs.version'])};"]
    # VCS binary ###
    flags += [f"{os.path.join(env['synopsys.synopsys_home'],'vcs',env['sim.vcs.version'])}/bin/vcs"]
    ### Common flags ###
    flags += ["-full64", "-override_timescale=1ps/1ps", "-sverilog", f"-Mdir={args.dir}", f"-o {os.path.join(args.dir, 'simv')}"]
    ### Debug + waveform ###
    flags += ["-debug_access+all"]
    ### Design input ###
    flags += ["-top", cfg["sim.inputs.tb_name"]]
    v_files = []
    for i in cfg["sim.inputs.input_files"] + cfg["sim.inputs.tb_input_files"]:
        if i not in  v_files:
            v_files.append(i)
    flags += v_files
    if "sim.inputs.tb_incdir" in cfg:
        flags += ["+incdir+" + i for i in cfg["sim.inputs.tb_incdir"]]
    if "sim.inputs.tb_defines" in cfg:
        flags += ["+define+" + i for i in cfg["sim.inputs.tb_defines"]]
    ### RTL SPECIFIC FLAGS ###
    if args.type == "rtl":
        pass
    ### RTL HARD SPECIFIC FLAGS ###
    elif args.type == "rtl-hard":
        flags += ["build/tech-sky130-cache/primitives.v", "build/tech-sky130-cache/sky130_fd_sc_hd.v"]
        flags += ["+define+FUNCTIONAL", "+define+UNIT_DELAY"]
        flags += ["+nospecify", "+notimingchecks"]
    ### SYN FUNCTIONAL SPECIFIC FLAGS ###
    elif args.type == "syn-functional":
        flags += ["build/tech-sky130-cache/primitives.v", "build/tech-sky130-cache/sky130_fd_sc_hd.v"]
        flags += ["+define+FUNCTIONAL", "+define+UNIT_DELAY"]
        flags += ["+nospecify", "+notimingchecks"]
    ### SYN SPECIFIC FLAGS ###
    elif args.type == "syn":
        flags += ["build/tech-sky130-cache/primitives.v", "build/tech-sky130-cache/sky130_fd_sc_hd.v"]
        flags += ["-sdf", f"max:{cfg['sim.inputs.top_module']}:{cfg['sim.inputs.sdf_file']}"]
        flags += ["+neg_tchk", "+sdfverbose", "-negdelay"]
        flags += ["+define+FUNCTIONAL", "+define+UNIT_DELAY"]
        flags += ["+warn=noSDFCOM_UHICD", "+warn=noSDFCOM_ANICD"]
    ### PAR FUNCTIONAL SPECIFIC FLAGS ###
    elif args.type == "par-functional":
        flags += ["build/tech-sky130-cache/primitives.v", "build/tech-sky130-cache/sky130_fd_sc_hd.v"]
        flags += ["+define+FUNCTIONAL", "+define+UNIT_DELAY"]
        flags += ["+nospecify", "+notimingchecks"]
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

