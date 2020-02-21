# This script has to be sourced in a shell and is thus NOT executable.
#
# Set up project
#
# Copyright (c) 2010-2017 The PyroScope Project <pyroscope.project@gmail.com>
#
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

SCRIPTNAME="$0"
test "$SCRIPTNAME" != "-bash" -a "$SCRIPTNAME" != "-/bin/bash" || SCRIPTNAME="${BASH_SOURCE[0]}"

export DEBFULLNAME=pyroscope
export DEBEMAIL=pyroscope.project@gmail.com

deactivate 2>/dev/null || true
test -z "$PYTHON" -a -x "/usr/bin/python3.8" && PYTHON="/usr/bin/python3.8"
test -z "$PYTHON" -a -x "/usr/bin/python3" && PYTHON="/usr/bin/python3"
test -z "$PYTHON" -a -x "/usr/bin/python2" && PYTHON="/usr/bin/python2"
test -z "$PYTHON" -a -x "/usr/bin/python" && PYTHON="/usr/bin/python"
test -z "$PYTHON" && PYTHON="python3"

pyvenv=.venv/$(basename $(builtin cd $(dirname "$SCRIPTNAME") && pwd))
test -x $pyvenv/bin/python || ${PYTHON} -m venv $pyvenv
grep DEBFULLNAME $pyvenv/bin/activate >/dev/null 2>&1 || cat >>$pyvenv/bin/activate <<EOF
export DEBFULLNAME=$DEBFULLNAME
export DEBEMAIL=$DEBEMAIL
EOF
. $pyvenv/bin/activate

for basepkg in pip setuptools wheel; do
    pip install -U $basepkg
done
python -c "import distribute" 2>/dev/null || pip uninstall -y distribute

pip install -r requirements-dev.txt
paver generate_setup
paver minilib
paver bootstrap
pip install -e .
