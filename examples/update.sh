#!/bin/sh

EXAMPLES=`dirname $0`
SEQDIAG=$EXAMPLES/../bin/seqdiag

for diag in `ls $EXAMPLES/*.diag`
do
    png=$EXAMPLES/`basename $diag .diag`.png
    echo $SEQDIAG -Tpng -o $png $diag
    $SEQDIAG -Tpng -o $png $diag
done
