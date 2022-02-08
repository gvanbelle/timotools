#!/bin/bash
#
# use: test.sh [nightID]
#     where nightID is in YYYYMMDD format
#
# Test for calibration data: flats, cals, logfiles
#
nightID="$1"
calRootDir="/mnt/c/Users/timo/OneDrive/Documents/ACP Astronomy/Images/"
fullRootDir="/mnt/c/Users/timo/OneDrive/Documents/ACP Astronomy/Images/Scheduler/Observatory Operator/"
calDataDir="$calRootDir$nightID"
fullDataDir="$fullRootDir$nightID"
echo "Testing for $calDataDir"
if [ -d "$calDataDir" ]
then
	echo "Directory exists"
else
	echo "Directory does not exist"
	exit 1
fi
#
# 
#
echo ""
echo "Moving calibration folders from $calDataDir to $fullDataDir."
#
calDataDirSource="$calDataDir/AutoFlat"
fullDataDirTarget="$fullDataDir"
echo "$calDataDirSource" "-->" "$fullDataDirTarget"
cp -rp "$calDataDirSource" "$fullDataDirTarget"
#
calDataDirSource="$calDataDir/Calibration"
fullDataDirTarget="$fullDataDir"
echo "$calDataDirSource" "-->" "$fullDataDirTarget"
cp -rp "$calDataDirSource" "$fullDataDirTarget"
#
calDataDirSource="$calDataDir/LogFiles"
fullDataDirTarget="$fullDataDir"
echo "$calDataDirSource" "-->" "$fullDataDirTarget"
cp -rp "$calDataDirSource" "$fullDataDirTarget"
#
cd "$fullDataDirTarget"
#
# Rename and compress the files
#
echo ""
echo "Fixing image file extensions from *.fts to *.fits."
find . -type f -name '*.fts' -print0 | xargs -0 rename 's/.fts$/.fits/'
#
echo "Compressing files from *.fits to *.fits.gz, please wait ..."
find . -depth -name "*.fits" -exec pigz -r *.fits {} +
#
# Copy the calibration tasks log files
#
echo ""
echo "Copy the log files."
logfileSourceRootDir="/mnt/c/Users/timo/OneDrive/Documents/ACP Astronomy/Logs/AutoFlat/"
logfileSourceDir="$logfileSourceRootDir$nightID"
logfileTarget="$fullDataDir/LogFiles"
#
echo "$logfileSourceDir" "-->" "$logfileTarget"
cp -rp "$logfileSourceDir/AutoFlat" "$logfileTarget"
#
# Copy the individual observing task log files
#
#C:\Users\timo\OneDrive\Documents\ACP Astronomy\Logs\Scheduler\Observatory Operator
#
tasklogSourceRootDir="/mnt/c/Users/timo/OneDrive/Documents/ACP Astronomy/Logs/Scheduler/Observatory Operator/"
tasklogSourceDir="$tasklogSourceRootDir$nightID"
tasklogTarget="$fullDataDir/LogFiles"
#
echo "$tasklogSourceDir" "-->" "$tasklogTarget"
cp -rp "$tasklogSourceDir" "$tasklogTarget"
#
# copy last 24 hours from C:\Users\timo\OneDrive\Documents\ACP Astronomy\Scheduler Engine Logs to above Logs folder
#
targetDate="${nightID:0:4}-${nightID:4:2}-${nightID:6:2}"
i=1
targetDatePlusOne=$(date +%Y-%m-%d -d "$targetDate + $i day")
targetDateTime="$targetDate 12:00:00"
targetDatePlusOneTime="$targetDatePlusOne 12:00:00"
schedulerLogsRootDir="/mnt/c/Users/timo/OneDrive/Documents/ACP Astronomy/Scheduler Engine Logs"
schedulerLogsTarget="$fullDataDir/LogFiles"
echo ""
echo "Copying scheduler engine logs from $targetDateTime - $targetDatePlusOneTime"
echo "Source: $schedulerLogsRootDir"
echo "Target: $schedulerLogsTarget"
cd "$schedulerLogsRootDir"
cp -p `find -newerct "$targetDateTime" ! -newerct "$targetDatePlusOneTime"` "$schedulerLogsTarget"
#
#
# copy all-sky images, make movie, clean up
#
cd "$fullDataDir"
mkdir "allsky-images"
allskyTargetDir="$fullDataDir/allsky-images"
allskyRootDir="/mnt/c/observing_data/all-sky cam"
cd "$allskyRootDir"
targetDateTime="$targetDate 19:00:00"
targetDatePlusOneTime="$targetDatePlusOne 07:00:00"
cp -p `find -newerct "$targetDateTime" ! -newerct "$targetDatePlusOneTime"` "$allskyTargetDir"
cd "$allskyTargetDir"
ffmpeg -framerate 25 -pattern_type glob -i "*.JPG" "allsky-$nightID.mp4"
tar -zcf "allsky-$nightID.tar.gz" *.JPG
rm *.JPG


