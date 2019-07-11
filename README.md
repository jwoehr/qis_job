# qis_job
QISKit Job Control

**`qis_job`** is an [IBM Q Experience](https://quantum-computing.ibm.com) argument-parsing job and experiment
execution script.

* `qasm_job.py` is the script. It is based on the [QISKit](https://github.com/Qiskit) API 2.
  * See earlier releases for API 1 support.
  * For this project you will need to install
    * [Qiskit/qiskit-terra](https://github.com/Qiskit/qiskit-terra)
    * [Qiskit/qiskit-aer](https://github.com/Qiskit/qiskit-aer)
    * An [IBM Q Experience API token](https://quantum-computing.ibm.com/account)
* Additionally, there are example qasm programs in the `qasm_examples` directory.

```
$ python qasm_job.py -h
usage: qasm_job.py [-h] [-i | -s | -a | -b BACKEND] [-c CREDITS] [-j] [-m]
                   [-o OUTFILE] [-p PROPERTIES] [-q QUBITS] [--qiskit_version]
                   [-r] [-t SHOTS] [-v] [-x] [--token TOKEN] [--url URL]
                   [filepaths [filepaths ...]]

qasm_job.py : Loads from one or more qasm source files and runs jobs with
reporting in CSV form. Also can give info on backend properties, qiskit
version, transpilation, etc. Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO
Box 51, Golden, CO 80402-0051. BSD-3 license -- See LICENSE which you should
have received with this code. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT
HOLDERS AND CONTRIBUTORS "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED
WARRANTIES.

positional arguments:
  filepaths             Filepath(s) to 1 or more .qasm files, default is stdin

optional arguments:
  -h, --help            show this help message and exit
  -i, --ibmq            Use best genuine IBMQ processor (default)
  -s, --sim             Use IBMQ qasm simulator
  -a, --aer             Use QISKit aer simulator
  -b BACKEND, --backend BACKEND
                        Use specified IBMQ backend
  -c CREDITS, --credits CREDITS
                        Max credits to expend on run, default is 3
  -j, --job             Print job dictionary
  -m, --memory          Print individual results of multishot experiment
  -o OUTFILE, --outfile OUTFILE
                        Write appending CSV to outfile, default is stdout
  -p PROPERTIES, --properties PROPERTIES
                        Print properties for specified backend to stdout and
                        exit 0
  -q QUBITS, --qubits QUBITS
                        Number of qubits for the experiment, default is 5
  --qiskit_version      Print Qiskit version and exit 0
  -r, --result          Print job result
  -t SHOTS, --shots SHOTS
                        Number of shots for the experiment, default 1024, max
                        8192
  -v, --verbose         Increase verbosity each -v up to 3
  -x, --transpile       Show circuit transpiled for chosen backend
  --token TOKEN         Use this token if a --url argument is also provided
  --url URL             Use this url if a --token argument is also provided
```

Jack Woehr 2019-07-11
