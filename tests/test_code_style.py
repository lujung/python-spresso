import os
import re
import subprocess
import unittest

py_dir = os.path.join(os.path.dirname(__file__), "..")

LINE_REGEX = re.compile(r"^([A-Za-z0-9._/\\]+):(\d+):(\d+): (\w+) (.*)$")


def pretty_print_output(lines):
    parsed_lines = (line.decode('utf-8').replace(py_dir, '')[1:] for line in
                    lines)
    parsed_lines = (LINE_REGEX.match(line).groups() for line in parsed_lines)

    files = {}
    for line in parsed_lines:
        py_file, row, col, num, msg = line
        files.setdefault(py_file, []).append((row, col, num, msg))

    for file, messages in files.items():
        yield "\033[1m%s:\033[0m" % file
        yield "|"

        content = open(os.path.join(py_dir, file)).readlines()

        for message in messages:
            line, col, num, msg = message
            cnt = content[int(line) - 1].replace("\n", "").strip()
            yield "|+ Error %s in line: %s(%s)" % (num, line, col)
            yield "|L (\033[91m%s\033[0m) %s" % (msg, cnt)
            yield "|"


class PackagePep8TestCase(unittest.TestCase):
    def test_code_style(self):
        p = subprocess.Popen(
            ["flake8",
             "--ignore=E121,E123,E124,E125,E126,E127,E128,F403,F999",
             "--exclude", "javascript",
             "--max-line-length=80",
             py_dir], stdout=subprocess.PIPE)

        out, err = p.communicate()
        errors = out.splitlines()

        if errors:
            if len(errors) == 1:
                self.fail("Found a style violation in the code base: \n\n" +
                          "\n".join(pretty_print_output(errors)))
            self.fail("Found %d style violations in the code base: \n\n" % len(
                errors) + "\n".join(pretty_print_output(errors)))
