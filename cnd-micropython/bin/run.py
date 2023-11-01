from sh import human
import os


def __main__(args):
	prog=""
	if len(args) > 2:
		prog = args[2]

	if prog:
		print("running {}".format(prog))

		with open(prog) as f:
		    code = f.read()
		exec(code)

	else:
		print("usage: run <program.py>")
