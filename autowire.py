#!/usr/bin/env python3
from argparse import ArgumentParser
from subprocess import Popen

parser = ArgumentParser()
parser.add_argument("--file")
parser.add_argument("--header")
args = parser.parse_args()
opened = False
pending = None

class APICall():
    def __init__(self, method_name):
        self.method_name = method_name
        self.args = []
        self.values = []

    def assign(self, name, value):
        for index, arg in enumerate(self.args):
            components = arg.split(" ")

            if name == components[1]:
                if len(self.values) < index:
                    for subindex in range(0, index):

                        self.values.append("NULL")

                self.values[index] = value

    def load_args(self, param_list):
        data = map(lambda x: x.strip(), param_list.split(","))
        self.args = list(data)

    def load_values(self, value_list):
        self.values = value_list

    def output(self):
        for arg in self.args:

            args = arg.split(" ")

            if "*" in arg:
                print("{} = malloc(sizeof {});".format(arg, args[-1]))

        param_list =  ", ".join(self.values)
        print("{}({});".format(self.method_name, param_list))


for line in open(args.file):
    if line == "\n":
        continue
    if ":" in line:
        if pending:
            pending.output()
            pending = None
        if opened:
            print("}")
        # method declaration
        definition, params = line.strip().split(":")
        return_type, name = definition.split(" ")

        all_params = params.split(" ")
        all_params.pop(0)
        param_list = ""
        for name, type in list(zip(*[iter(all_params)]*2))[:-1]:
            param_list += "{} {},".format(name, type)
        if len(all_params) > 1:
            param_list += "{} {}".format(all_params[-2], all_params[-1])
        print("{} {}({}) {{".format(return_type, name, param_list))
        opened = True
    elif line[0] == "\t":
        # continuation line
        defs = line.strip().split(" ")
        for definition in defs:
            name, value = definition.split("=")
            pending.assign(name, value)
        pending.output()
        pending = None
    else:
        if pending:
            pending.output()
        # print(line)
        params = line.strip().split(" ")
        method_name = params[0]
        found = False
        header_def = ""
        # print("Looking for {}.".format(method_name))
        for header_line in open(args.header):
            inserted = False
            if method_name in header_line:
                found = True
                inserted = True
                header_def += header_line
            if found and ")" in header_line:
                if not inserted:
                    header_def += header_line
                break
            if found and inserted == False:
                header_def += header_line

        definition = " ".join(map(lambda x: x.strip(), header_def.split("\n")))
        # print(header_def)
        try:
            start_pos = definition.index("(") + 1
            end_pos = definition.index(")")
            param_list = definition[start_pos:end_pos]
        except ValueError:
            print("Not found")

        pending = APICall(method_name)
        pending.load_args(param_list)
        pending.load_values(params[1:])



if pending:
    pending.output()
    pending = None
if opened:
    print("}")
