"""qasm_job.py
Load from qasm source and run job with reporting
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES."""

import argparse
import datetime
import pprint
import sys

from qiskit import IBMQ
from qiskit import QuantumCircuit
from qiskit import execute
try:
    from qiskit import __qiskit_version__
except ImportError:
    print("qasm_job WARNING: --qiskit_version not available this qiskit level")
try:
    from qiskit.compiler import transpile
except ImportError:
    print("qasm_job WARNING: -x,--transpile not available this qiskit level")
from qiskit.tools.monitor import job_monitor


explanation = """qasm_job.py : Load from qasm source and run job with reporting
in CSV form.
Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.
BSD-3 license -- See LICENSE which you should have received with this code.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.
"""
parser = argparse.ArgumentParser(description=explanation)
group = parser.add_mutually_exclusive_group()
group.add_argument("-i", "--ibmq", action="store_true",
                   help="Use best genuine IBMQ processor (default)")
group.add_argument("-s", "--sim", action="store_true",
                   help="Use IBMQ qasm simulator")
group.add_argument("-a", "--aer", action="store_true",
                   help="Use QISKit aer simulator")
group.add_argument("-b", "--backend", action="store",
                   help="Use specified IBMQ backend")
parser.add_argument("-c", "--credits", type=int, action="store", default=3,
                    help="Max credits to expend on run, default is 3")
parser.add_argument("-j", "--job", action="store_true",
                    help="Print job dictionary")
parser.add_argument("-m", "--memory", action="store_true",
                    help="Print individual results of multishot experiment")
parser.add_argument("-o", "--outfile", action="store",
                    help="Write appending CSV to outfile, default is stdout")
parser.add_argument("-p", "--properties", action="store",
                    help="Print properties for specified backend to stdout and exit 0")
parser.add_argument("-q", "--qubits", type=int, action="store", default=5,
                    help="Number of qubits for the experiment, default is 5")
parser.add_argument("--qiskit_version", action="store_true",
                    help="Print Qiskit version and exit 0")
parser.add_argument("-r", "--result", action="store_true",
                    help="Print job result")
parser.add_argument("-t", "--shots", type=int, action="store", default=1024,
                    help="Number of shots for the experiment, default 1024, max 8192")
parser.add_argument("-v", "--verbose", action="count", default=0,
                    help="Increase verbosity each -v up to 3")
parser.add_argument("-x", "--transpile", action="store_true",
                    help="Show circuit transpiled for chosen backend")
parser.add_argument("--token", action="store",
                    help="Use this token if a --url argument is also provided")
parser.add_argument("--url", action="store",
                    help="Use this url if a --token argument is also provided")
parser.add_argument("filepaths", nargs='*',
                    help="Filepath(s) to .qasm file, default is stdin")

args = parser.parse_args()

if (args.token and not args.url) or (args.url and not args.token):
    print('--token and --url must be used together or not at all', file=sys.stderr)
    exit(1)

# Utility functions
# #################


def verbosity(text, count):
    """Print text if count exceeds verbose level"""
    if args.verbose >= count:
        print(text)


def account_fu(token, url):
    """Load account appropriately and return provider"""
    if token:
        p = IBMQ.enable_account(token, url=url)
    else:
        p = IBMQ.load_account()
    return p


def csv_str(description, sort_keys, sort_counts):
    """Generate a cvs as a string from sorted keys and sorted counts"""
    csv = []
    csv.append(description)
    keys = ""
    for key in sort_keys:
        keys += key + ';'
    csv.append(keys)
    counts = ""
    for count in sort_counts:
        counts += str(count) + ';'
    csv.append(counts)
    return csv

# Choose backend
# ##############


def choose_backend(aer, token, url, b_end, sim, qubits):
    """Return backend selected by user if account will activate and allow."""
    backend = None
    if aer:
        # Import Aer
        from qiskit import BasicAer
        # Run the quantum circuit on a statevector simulator backend
        backend = BasicAer.get_backend('statevector_simulator')
    else:
        provider = account_fu(token, url)
        verbosity("Provider is " + str(provider), 3)
        verbosity("provider.backends is " + str(provider.backends()), 3)
        if b_end:
            backend = provider.get_backend(b_end)
            verbosity('b_end provider.get_backend() returns ' + str(backend), 3) 
        elif sim:
            backend = provider.get_backend('ibmq_qasm_simulator')
            verbosity('sim provider.get_backend() returns ' + str(backend), 3)
        else:
            from qiskit.providers.ibmq import least_busy
            large_enough_devices = provider.backends(
                filters=lambda x: x.configuration().n_qubits >= qubits
                and not x.configuration().simulator)
            backend = least_busy(large_enough_devices)
            verbosity("The best backend is " + backend.name(), 2)
    verbosity("Backend is " + str(backend), 1)
    return backend


# Do job loop
# ###########

def one_job(filepath, backend, outfile, xpile, shots, memory, j_b, res):
    """Load qasm and run the job, print csv and other selected output"""

    if filepath is None:
        filepath = sys.stdin
    if outfile is None:
        outfile = sys.stdout

    if backend is None:
        print("No backend available, quitting.")
        exit(100)

    # Get file
    verbosity("File path is " + ("stdin" if filepath is sys.stdin else filepath), 2)
    ifh = filepath if filepath is sys.stdin else open(filepath, "r")
    verbosity("File handle is " + str(ifh), 3)

    # Read source
    qasm_source = ifh.read()
    ifh.close()
    verbosity("qasm source:\n" + qasm_source, 1)

    # Create circuit
    circ = QuantumCircuit.from_qasm_str(qasm_source)
    verbosity(circ.draw(), 2)

    # Transpile if requested and available and show transpiled circuit
    # ################################################################

    if xpile:
        try:
            print(transpile(circ, backend=backend))
        except NameError:
            print('Transpiler not available this Qiskit level.', file=sys.stderr)

    # Prepare job
    # ###########

    # Maximum number of credits to spend on executions.
    max_credits = args.credits

    # Execute
    job_exp = execute(circ, backend=backend, shots=shots,
                  max_credits=max_credits, memory=memory)
    if j_b:
        print(job_exp)

    job_monitor(job_exp)
    result_exp = job_exp.result()

    if res:
        print(result_exp)

    counts_exp = result_exp.get_counts(circ)
    verbosity(counts_exp, 1)
    sorted_keys = sorted(counts_exp.keys())
    sorted_counts = []
    for i in sorted_keys:
        sorted_counts.append(counts_exp.get(i))

    # Raw data if requested
    if memory:
        print(result_exp.data())

    # Generate CSV
    output = csv_str(str(backend) + ' ' + datetime.datetime.now().isoformat(),
                     sorted_keys, sorted_counts)

    # Open outfile
    verbosity("Outfile is " + ("stdout" if outfile is sys.stdout else outfile), 2)
    ofh = outfile if outfile is sys.stdout else open(outfile, "a")
    verbosity("File handle is " + str(ofh), 3)

    # Write CSV
    for line in output:
        ofh.write(line + '\n')
    if outfile is not sys.stdout:
        ofh.close()

# ####
# Main
# ####

# Informational queries
# #####################

if args.properties:
    provider = account_fu(args.token, args.url)
    backend = provider.get_backend(args.properties)
    pp = pprint.PrettyPrinter(indent=4, stream=sys.stdout)
    pp.pprint(backend.properties())
    exit(0)

if args.qiskit_version:
    try:
        __qiskit_version__
    except NameError:
        print("__qiskit_version__ not present in this Qiskit level.")
        exit(1)
    pp = pprint.PrettyPrinter(indent=4, stream=sys.stdout)
    pp.pprint(__qiskit_version__)
    exit(0)

backend = choose_backend(args.aer, args.token, args.url,
    args.backend, args.sim, args.qubits)

if not args.filepaths:
    one_job(None, backend, args.outfile, args.transpile,
        args.shots, args.memory, args.job, args.result)
else:
    for filepath in args.filepaths:
        one_job(filepath, backend, args.outfile, args.transpile,
            args.shots, args.memory, args.job, args.result)

verbosity('Done!', 1)

# End