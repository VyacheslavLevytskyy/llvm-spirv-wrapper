#!/usr/bin/python3
#

import os, subprocess, sys
from shutil import copyfile
from pathlib import Path

EXT = [
  'SPV_INTEL_bfloat16_conversion',
  'SPV_KHR_float_controls',
  'SPV_INTEL_variable_length_array',
  'SPV_KHR_subgroup_rotate',
  'SPV_INTEL_usm_storage_classes',
  'SPV_KHR_uniform_group_instructions',
  'SPV_EXT_shader_atomic_float_add',
  'SPV_EXT_shader_atomic_float16_add',
  'SPV_EXT_shader_atomic_float_min_max',
  'SPV_KHR_linkonce_odr',
  'SPV_INTEL_function_pointers',
  'SPV_INTEL_subgroups',
  'SPV_INTEL_arbitrary_precision_integers',
  'SPV_INTEL_optnone',
  'SPV_KHR_no_integer_wrap_decoration',
  'SPV_KHR_expect_assume',
  'SPV_KHR_bit_instructions',
]

# Please change paths to match your environment
# ===
PREFIX = "/YOUR_ROOT/"
LLC = PREFIX + "llvm-project/build/bin/llc"
BACK = PREFIX + "khronos-llvm-spirv/build/tools/llvm-spirv/llvm-spirv"
VALID = PREFIX + "spirv-tools/bin/spirv-val"
STORE_BACKUP_TO = PREFIX + "test-files-to-backup/"
# ===

def parse_args(args):
  pos, named, key = [], {}, None
  for arg in args:
    if key:
      if arg.startswith('-') and len(arg) > 2:
        named[key] = True
        l = arg[1:].split("=")
        if len(l) == 1:
          named[arg[1:]] = True
        else:
          [key, value] = l
          named[key] = value
        key = None
      elif arg.startswith('-') and len(arg) == 2:
        named[key] = True
        key = arg[1:]
      else:
        named[key] = arg
        key = None
    elif arg.startswith('-') and len(arg) > 2:
      l = arg[1:].split("=")
      if len(l) == 1:
        named[arg[1:]] = True
      else:
        [key, value] = l
        named[key] = value
      key = None
    elif arg.startswith('-') and len(arg) == 2:
      key = arg[1:]
    else:
      pos.append(arg)
  if key:
    named[key] = True
  if 'spirv-ext' in named:
    ext = ['+%s' % s[1:] for s in named['spirv-ext'].split(",") if len(s) > 1 and s[0] == '+' and s[1:] in EXT]
    ext = ['--spirv-ext=+SPV_KHR_bit_instructions,%s' % ",".join(ext)]
  else:
    ext = ["--spirv-ext=+SPV_KHR_bit_instructions"]
  if 'o' not in named or named['o'] == '-':
    return None
  return [
    LLC,
    "" if len(pos) == 0 else pos[0],
    "-o",
    named['o'],
    "-filetype=obj",
    "-mtriple=spirv64-unknown-unknown",
    "-O0",
    "--avoid-spirv-capabilities=Shader",
    "--translator-compatibility-mode",
  ] + ext

if __name__ == "__main__":
  cmd = parse_args(sys.argv[1:])
  if cmd is None:
    sys.exit(-1)
  cmd_str = ' '.join(cmd)
  print(cmd_str)
  in_file = os.path.basename(cmd[1])
  in_file_bak = STORE_BACKUP_TO + in_file
  copyfile(cmd[1], in_file_bak)
  try:
    print('%' * 80)
    subprocess.run(cmd, check=True, capture_output=True)
    print('.' * 20)
    print('... complete run')
    out_file = os.path.basename(cmd[3])
    out_bak = STORE_BACKUP_TO + out_file
    copyfile(cmd[3], out_bak)
    print('.' * 20)
    print('... complete copy')
    print("Repeat with CMD:")
    cmd[1] = in_file_bak
    cmd[3] = out_bak
    cmd[4] = ""
    print(' '.join(cmd))
    subprocess.run([VALID, out_bak], check=True, capture_output=True)
    print('.' * 20)
    print('... complete validation')
    cmd_back = [
      BACK,
      "-r", out_bak,
    ]
    subprocess.run(cmd_back, check=True, capture_output=True)
    print('.' * 20)
    print('... complete reverse')
    print('%' * 80)
  except subprocess.CalledProcessError as err:
    err_msg = err.stderr.decode("utf-8")
    print(err_msg)
