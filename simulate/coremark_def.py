COREMARK_PATH = "/home/jw38176/gem5/jw38176/tests/mical_binaries/builds/linux64/gcc64/bin/"

coremark_benchmarks = {
    "cjpeg" : "cjpeg-rose7-preset.exe",
    "core" : "core.exe",
    "linear" : "linear_alg-mid-100x100-sp.exe",
    "loops" : "loops-all-mid-10k-sp.exe",
    "nnet": "nnet_test.exe",
    "parser" : "parser-125k.exe",
    "radix2" : "radix2-big-64k.exe",
    "sha" : "sha-test.exe",
    "zip" : "zip-test.exe"
}

coremark_args = ["-v0", "-c1", "-w1", "-i1"]







