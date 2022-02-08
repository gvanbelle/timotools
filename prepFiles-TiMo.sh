for f in *; do mv "$f" `echo $f | tr ' ' '_'`; done		# remove spaces
for f in *; do mv "$f" `echo $f | tr '-' '_'`; done		# remove dashes
for f in *; do mv "$f" `echo $f | tr "'" '_'`; done		# remove 's
for f in *.fts; do mv -- "$f" "${f%.fts}.fits"; done	# change extension from 'fts' to 'fits'
sethead *fits INSTRUME='TIMOG3'							# sethead part of WCStools
