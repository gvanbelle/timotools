find . -type f -name '*.fts' -print0 | xargs -0 rename 's/.fts$/.fits/'
find . -depth -name "*.fits" -exec pigz -r *.fits {} +

