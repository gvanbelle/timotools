find . -type f -name '*.new' -print0 | xargs -0 rename 's/.new$/.new.fits/'
find . -depth -name "*.fits" -exec pigz -r *.fits {} +
rm *.solved
rm *.match
rm *.rdls
rm *.corr
rm *.wcs
rm *.axy
rm *.xyls

