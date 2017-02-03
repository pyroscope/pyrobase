# -*- coding: utf-8 -*-
# pylint: disable=
""" Paver Task Implementation Helpers.

    Copyright (c) 2011 The PyroScope Project <pyroscope.project@gmail.com>
"""
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
import os
import sys
import pkg_resources

from paver import easy, tasks
from pyrobase import iterutil


def venv_bin(name=None):
    """ Get the directory for virtualenv stubs, or a full executable path
        if C{name} is provided.
    """
    if not hasattr(sys, "real_prefix"):
        easy.error("ERROR: '%s' is not a virtualenv" % (sys.executable,))
        sys.exit(1)

    for bindir in ("bin", "Scripts"):
        bindir = os.path.join(sys.prefix, bindir)
        if os.path.exists(bindir):
            if name:
                return os.path.join(bindir, name + os.path.splitext(sys.executable)[1])
            else:
                return bindir

    easy.error("ERROR: Scripts directory not found in '%s'" % (sys.prefix,))
    sys.exit(1)


def vsh(cmd, *args, **kw):
    """ Execute a command installed into the active virtualenv.
    """
    args = '" "'.join(i.replace('"', r'\"') for i in args)
    easy.sh('"%s" "%s"' % (venv_bin(cmd), args))


def install_tools(dependencies):
    """ Install a required tool before using it, if it's missing.

        Note that C{dependencies} can be a distutils requirement,
        or a simple name from the C{tools} task configuration, or
        a (nested) list of such requirements.
    """
    tools = getattr(easy.options, "tools", {})
    for dependency in iterutil.flatten(dependencies):
        dependency = tools.get(dependency, dependency)
        try:
            pkg_resources.require(dependency)
        except pkg_resources.DistributionNotFound:
            vsh("pip", "install", "-q", dependency)
            dependency = pkg_resources.require(dependency)
            easy.info("Installed required tool %s" % (dependency,))


def task_requires(*dependencies):
    """ A task decorator that ensures a distutils dependency (or a list thereof) is met
        before that task is executed.
    """
    def entangle(task):
        "Decorator wrapper."
        if not isinstance(task, tasks.Task):
            task = tasks.Task(task)

        def tool_task(*args, **kw):
            "Install requirements, then call original task."
            install_tools(dependencies)
            return task_body(*args, **kw)

        # Apply our wrapper to original task
        task_body, task.func = task.func, tool_task
        return task

    return entangle


def toplevel_packages():
    """ Get package list, without sub-packages.
    """
    packages = set(easy.options.setup.packages)
    for pkg in list(packages):
        packages -= set(p for p in packages if str(p).startswith(pkg + '.'))
    return list(sorted(packages))
