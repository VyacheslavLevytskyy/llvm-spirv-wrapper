# llvm-spirv-wrapper

A wrapper to allow running SPIR-V Backend instead of llvm-spirv in SYCL end-to-end tests

# Steps

1. Change paths according to your environment
2. Rename to `llvm-spirv` and replace the same executable from `llvm/build/bin`, after backuping the original file.
3. Run as usual, e.g., ./bin/llvm-lit ../sycl/test-e2e/ -v
