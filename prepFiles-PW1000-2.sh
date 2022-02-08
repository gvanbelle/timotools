#for f in *; do mv "$f" `echo $f | tr ' ' '_'`; done            # remove spaces
#for f in *; do mv "$f" `echo $f | tr '-' '_'`; done            # remove dashes
#for f in *; do mv "$f" `echo $f | tr "'" '_'`; done            # remove 's
# for f in *.fts; do mv -- "$f" "${f%.fts}.fits"; done  # change extension from 'fts' to 'fits'
#sethead *fits INSTRUME='PW2ALTA'                                               # sethead is part of wcstools
#
# this is better, works recursively
#
find . -type f -name '*.fts' -exec rename 's/fts/fits/g' {} \;
find . -type f -name '*.fits' -exec rename 's/ /\_/g' {} \;
find . -type f -name '*.fits' -exec rename 's/-/\_/g' {} \;
find . -type f -name '*.fits' -exec rename "s/\'/\_/g" {} \;
find . -type f -name '*.fits' -exec sethead {} INSTRUME='PW2ALTA' \;
find . -type f -name '*.fits' -exec sethead {} FILTER='NoFilt' \;

