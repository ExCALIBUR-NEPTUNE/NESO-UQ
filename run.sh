#!/usr/bin/env bash

#Script to run NESO and call post processing script to
#create json file of data for use by EasyVVUQ
#accepts one argument - the input file e.g. neso.xml 

# make sure executable (available from 
# https://github.com/ExCALIBUR-NEPTUNE/NESO)
# is in PATH or edit to provide complete path
EXEC=Electrostatic2D3V
# Edit these variables to point to location of
# the mesh and post processing script (included in repo)
ROOT_DIR=/path/to/repo
PYFILE=${ROOT_DIR}/python/extract_last_evaluations.py
MESH=${ROOT_DIR}/examples/two_stream/two_stream_mesh.xml
export OMP_NUM_THREADS=1
# Edit run command as appropriate for your system
mpirun -n 4 -map-by core -bind-to hwthread ${EXEC} $1 ${MESH}  > /dev/null
echo "Run complete"
python3 ${PYFILE} Electrostatic2D3V_line_field_evaluations.h5part >output.json
