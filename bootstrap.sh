# Set up project
SCRIPTNAME="$0"
test "$SCRIPTNAME" != "-bash" -a "$SCRIPTNAME" != "-/bin/bash" || SCRIPTNAME="${BASH_SOURCE[0]}"

deactivate 2>/dev/null || true
pyvenv=.pyvenv/$(basename $(builtin cd $(dirname "$SCRIPTNAME") && pwd))
test -x $pyvenv/bin/python || ${VIRTUALENV:-/usr/bin/virtualenv} $pyvenv
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
