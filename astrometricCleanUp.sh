#! /bin/bash
if [ -d astrometric ]
then
	cd astrometric
else 
	mkdir astrometric
	cd astrometric
fi
cd ..

if [ -d AutoFlat ]
then
	cd astrometric
	mkdir AutoFlat
	cd ..
	cd AutoFlat
	find . -type f -size +16M -exec mv "{}" ../astrometric/AutoFlat/ \;
	cd ..
fi

if [ -d Calibration ]
then
	cd astrometric
	mkdir Calibration
	cd ..
	cd Calibration
	find . -type f -size +16M -exec mv "{}" ../astrometric/Calibration/ \;
	cd ..
fi

if [ -d clear ]
then
	cd astrometric
	mkdir clear
	cd ..
	cd clear
	find . -type f -size +16M -exec mv "{}" ../astrometric/clear/ \;
	cd ..
fi

if [ -d Johnson-U ]
then
	cd astrometric
	mkdir Johnson-U
	cd ..
	cd Johnson-U
	find . -type f -size +16M -exec mv "{}" ../astrometric/Johnson-U/ \;
	cd ..
fi

if [ -d Johnson-B ]
then
	cd astrometric
	mkdir Johnson-B
	cd ..
	cd Johnson-B
	find . -type f -size +16M -exec mv "{}" ../astrometric/Johnson-B/ \;
	cd ..
fi

if [ -d Johnson-V ]
then
	cd astrometric
	mkdir Johnson-V
	cd ..
	cd Johnson-V
	find . -type f -size +16M -exec mv "{}" ../astrometric/Johnson-V/ \;
	cd ..
fi

if [ -d Johnson-R ]
then
	cd astrometric
	mkdir Johnson-R
	cd ..
	cd Johnson-R
	find . -type f -size +16M -exec mv "{}" ../astrometric/Johnson-R/ \;
	cd ..
fi

if [ -d Johnson-I ]
then
	cd astrometric
	mkdir Johnson-I
	cd ..
	cd Johnson-I
	find . -type f -size +16M -exec mv "{}" ../astrometric/Johnson-I/ \;
	cd ..
fi

if [ -d Sloan-u ]
then
	cd astrometric
	mkdir Sloan-u
	cd ..
	cd Sloan-u
	find . -type f -size +16M -exec mv "{}" ../astrometric/Sloan-u/ \;
	cd ..
fi

if [ -d Sloan-g ]
then
	cd astrometric
	mkdir Sloan-g
	cd ..
	cd Sloan-g
	find . -type f -size +16M -exec mv "{}" ../astrometric/Sloan-g/ \;
	cd ..
fi

if [ -d Sloan-r ]
then
	cd astrometric
	mkdir Sloan-r
	cd ..
	cd Sloan-r
	find . -type f -size +16M -exec mv "{}" ../astrometric/Sloan-r/ \;
	cd ..
fi

if [ -d Sloan-i ]
then
	cd astrometric
	mkdir Sloan-i
	cd ..
	cd Sloan-i
	find . -type f -size +16M -exec mv "{}" ../astrometric/Sloan-i/ \;
	cd ..
fi

if [ -d Sloan-z ]
then
	cd astrometric
	mkdir Sloan-z
	cd ..
	cd Sloan-z
	find . -type f -size +16M -exec mv "{}" ../astrometric/Sloan-z/ \;
	cd ..
fi



