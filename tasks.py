# -*- coding: utf-8 -*-
#
# Project Tasks
#
from __future__ import print_function, unicode_literals

import os
import sys
import time
import shutil
import contextlib
import subprocess
import webbrowser

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from invoke import task


PROJECT_NAME = 'pyrobase'
PYTEST_CMD = 'python -m pytest'
SPHINX_AUTOBUILD_PORT = int(os.environ.get('SPHINX_AUTOBUILD_PORT', '8340'))


@contextlib.contextmanager
def pushd(folder):
    """Context manager to temporarily change directory."""
    cwd = os.getcwd()
    try:
        os.chdir(folder)
        yield folder
    finally:
        os.chdir(cwd)


@task
def test(ctx):
    """Run unit tests."""
    ctx.run(PYTEST_CMD)


@task
def cov(ctx):
    """Run unit tests & show coverage report."""
    coverage_index = Path("build/coverage/index.html")
    coverage_index.unlink()
    ctx.run(PYTEST_CMD)
    coverage_index.exists() and webbrowser.open(
        'file://{}'.format(os.path.abspath(coverage_index)))


@task(help={
    'output': 'Create report file (.html, .log, or .txt) [stdout]',
    'rcfile': 'Configuration file [./pylint.cfg]',
    'with-report': 'Include summary report',
})
def lint(ctx, output='', rcfile='', with_report=False):
    """Report pylint results."""
    # report according to file extension
    report_formats = {
        ".html": "html",
        ".log": "parseable",
        ".txt": "text",
    }

    lint_build_dir = Path("build/lint")
    lint_build_dir.exists() or lint_build_dir.makedirs()  # pylint: disable=expression-not-assigned

    argv = []
    if not rcfile and Path("pylint.cfg").exists():
        rcfile = "pylint.cfg"
    if rcfile:
        argv += ["--rcfile", os.path.abspath(rcfile)]
    if not with_report:
        argv += ["-rn"]
    argv += [
        "--import-graph", str((lint_build_dir / "imports.dot").resolve()),
    ]
    argv += [PROJECT_NAME]

    sys.stderr.write("Running %s::pylint '%s'\n" % (sys.argv[0], "' '".join(argv)))
    outfile = output
    if outfile:
        outfile = os.path.abspath(outfile)

    try:
        with pushd("src" if Path("src").exists() else "."):
            if outfile:
                argv.extend(["-f", report_formats.get(Path(outfile).ext, "text")])
                sys.stderr.write("Writing output to %r\n" % (str(outfile),))
                with open(outfile, "w", encoding='utf-8') as outhandle:
                    subprocess.check_call(["pylint"] + argv, stdout=outhandle)
            else:
                subprocess.check_call(["pylint"] + argv, )
        sys.stderr.write("invoke::lint - No problems found.\n")
    except subprocess.CalledProcessError as exc:
        if exc.returncode & 32:
            # usage error (internal error in this code)
            sys.stderr.write("invoke::lint - Usage error, bad arguments %r?!\n" % (argv,))
            sys.exit(exc.returncode)
        else:
            bits = {
                1: "fatal",
                2: "error",
                4: "warning",
                8: "refactor",
                16: "convention",
            }
            sys.stderr.write("invoke::lint - Some %s message(s) issued.\n" % (
                ", ".join([text for bit, text in bits.items() if exc.returncode & bit])
            ))
            if exc.returncode & 3:
                sys.stderr.write("invoke::lint - Exiting due to fatal / error message.\n")
                sys.exit(exc.returncode)


def watchdog_pid(ctx):
    """Get watchdog PID via ``netstat``."""
    result = ctx.run('netstat -tulpn 2>/dev/null | grep 127.0.0.1:{:d}'
                     .format(SPHINX_AUTOBUILD_PORT), warn=True, pty=False)
    pid = result.stdout.strip()
    pid = pid.split()[-1] if pid else None
    pid = pid.split('/', 1)[0] if pid and pid != '-' else None

    return pid


@task(help={
    'open-tab': "Open docs in new browser tab after initial build"
})
def docs(ctx, open_tab=False):
    """Start watchdog to build the Sphinx docs."""
    build_dir = 'docs/_build'
    index_html = build_dir + '/html/index.html'

    stop(ctx)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    ctx.run('command cd docs >/dev/null'
            ' && sphinx-apidoc -o apidoc -f -T ../src/' + PROJECT_NAME)

    print("\n*** Generating HTML doc ***\n")
    subprocess.check_call(
        'command cd docs >/dev/null'
        ' && . {pwd}/.venv/{prjname}/bin/activate'
        ' && nohup {pwd}/docs/Makefile SPHINXBUILD="sphinx-autobuild -p {port:d}'
        '          -i \'.*\' -i \'*.log\' -i \'*.png\' -i \'*.txt\'" html >autobuild.log 2>&1 &'
        .format(port=SPHINX_AUTOBUILD_PORT, pwd=os.getcwd(), prjname=PROJECT_NAME), shell=True)

    for i in range(25):
        time.sleep(2.5)
        pid = watchdog_pid(ctx)
        if pid:
            ctx.run("touch docs/index.rst")
            ctx.run('ps {}'.format(pid), pty=False)
            url = 'http://localhost:{port:d}/'.format(port=SPHINX_AUTOBUILD_PORT)
            if open_tab:
                webbrowser.open_new_tab(url)
            else:
                print("\n*** Open '{}' in your browser...".format(url))
            break


@task
def stop(ctx):
    "Stop Sphinx watchdog."
    print("\n*** Stopping watchdog ***\n")
    for i in range(4):
        pid = watchdog_pid(ctx)
        if not pid:
            break
        else:
            if not i:
                ctx.run('ps {}'.format(pid), pty=False)
            ctx.run('kill {}'.format(pid), pty=False)
            time.sleep(.5)
