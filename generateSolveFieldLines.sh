#
# generateSolveFieldLines.sh [wildcard]
#


for var in "$@"
do
    echo -e "solve-field \"$var\" --no-plots --scale-units arcsecperpix --scale-low 0.5 --scale-high 0.55"
done


