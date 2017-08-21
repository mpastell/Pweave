#!/bin/bash
N=6000

DIR=`mktemp -d`

python --version
pweave --version
echo "WRITING TO $DIR"

for i in `seq 1 1 $N`;
do
  echo "RUN #$i/$N"

  RUNDIR=$DIR/$i
  mkdir $RUNDIR

  OUTPUT=$RUNDIR/nondeterministicFail.tex
  STDOUT=$RUNDIR/out.txt
  STDERR=$RUNDIR/err.txt

  pweave -f tex -o $OUTPUT weave/tex/nondeterministicFail.texw > $STDOUT 2> $STDERR

  if [ -s $OUTPUT ]
  then
    if cmp $OUTPUT weave/tex/nondeterministicFail_REF.tex
    then
      grep "RuntimeError" $STDOUT $STDERR
    else
      echo "OUTPUT DIFFERS"
      diff $OUTPUT weave/tex/nondeterministicFail_REF.tex
    fi
  else
    echo "NO OUTPUT"
    echo "CHECK $STDOUT and $STDERR for details"
    break
  fi

  rm -r $RUNDIR

done

python --version
pweave --version
