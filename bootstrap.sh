# Set up project
test -x ./bin/python || ${VIRUALENV:-/usr/bin/virtualenv} .
. bin/activate
pip install -r requirements-dev.txt
paver generate_setup
paver minilib
paver bootstrap
