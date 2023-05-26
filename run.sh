#!/usr/bin/env bash
# Edit these variables to point to location of
# the mesh and post processing script (included in repo)
# and the neso executable available from 
# https://github.com/ExCALIBUR-NEPTUNE/NESO
EXEC=/path/to/Electrostatic2D3V.x
PYFILE=/path/to/post_process.py
MESH=/path/to/two_stream_mesh.xml
export OMP_NUM_THREADS=1
# Edit run command as appropriate
mpirun -n 4 -map-by core -bind-to hwthread ${EXEC} $1 ${MESH} > /dev/null
#Using awk to create a "fake" json output so can use easyvvuq JSON decoder
python3 ${PYFILE} $1 Electrostatic2D3V_field_trajectory.h5 | \
    awk '/Gradient/ {printf("{\"Gradient\" : %s}\n",$3)}' | tee output.json
