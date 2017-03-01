import os
import subprocess
import sys
import unittest

from coverage import coverage

# Insert template_context for test cases
sys.path.insert(0, os.path.abspath('..'))


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def get_test_suite():
    return unittest.TestLoader().discover(".", pattern="test_*.py")


def run_tests():
    unittest.TextTestRunner(verbosity=2).run(get_test_suite())


def create_rsa_key_pair(private_key_file, public_key_file):
    p = subprocess.Popen(
        ['openssl', 'genrsa', '-out', private_key_file, '2048'])
    p.wait()
    p = subprocess.Popen(
        ['openssl', 'rsa', '-pubout', '-in', private_key_file, '-out',
         public_key_file])
    p.wait()


def remove_rsa_key_pair(private_key_file, public_key_file):
    os.remove(os.path.abspath(private_key_file))
    os.remove(os.path.abspath(public_key_file))


def run_coverage():
    # Set up coverage
    cov = coverage(config_file=find(".coveragerc", "."))
    cov.start()
    suite = get_test_suite()

    # Exclude code style test
    for test_suite in suite:
        for tests in test_suite:
            for test in tests:
                if test.id().endswith('test_code_style'):
                    setattr(test, 'setUp',
                            lambda: test.skipTest(
                                'Prevent coverage result distortion'))

    unittest.TextTestRunner(verbosity=2).run(suite)

    # Stop coverage and print report
    cov.stop()
    cov.save()
    # cov.html_report()
    cov.report()
    cov.erase()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        exit()

    private_key_path = 'test_priv_key.pem'
    public_key_path = 'test_pub_key.pem'

    create_rsa_key_pair(private_key_path, public_key_path)

    if sys.argv[1] == "test":
        # Run all available tests
        run_tests()

    if sys.argv[1] == "coverage":
        # Run functional tests and print coverage report
        run_coverage()

    remove_rsa_key_pair(private_key_path, public_key_path)
