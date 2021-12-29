#!/bin/bash

# Update data files in github repo

# git clone https://github.com/Simon-Dixon/DigThatLick.git
# cd DigThatLick/
vi DATA/DTLtoJE_instruments.csv 
vi DATA/orig2DTL_instruments.csv 
git commit -a -m "Corrected errors in instrument files ; fixes #1"
git push

# Update to latest versions 
cd DATA/
cp -p ~/jazz/DTL1000/DTL1000-metadata-20211202/*json DTL1000_1960-2020_json_v0/.
cp -p ~/jazz/DTL1000/dtl_1000-2021-12-17a.json dtl_1000.json 
#although segmentations are not used by Polina's code, they are in DATA
cp -p ../../../DTL1000/DTL_1000_segmentations-20211213.csv DTL_1000_segmentations.csv
cp -p ~/jazz/DTL1000/dtl_metadata_with_corrections.xlsx .
cp -p ~/jazz/DTL1000/id_dtl1000.csv .
diff ~/jazz/DTL1000/id_dtl1000_idonly.csv .
cp -p ~/jazz/JazzEncyclopedia/JECompleteIndex_20211229.csv JECompleteIndex_cleaned.csv 
diff ~/jazz/DTL1000/LJpeople.nt .
cp -p ~/jazz/DTL1000/ErrorCorrection.log metadataErrors.txt 
cp -p ~/jazz/DTL1000/missing_performer-20211221.csv missing_performer.csv 
cp -p ~/jazz/DTL1000/solo_extract_meta-20211213.csv solo_extract_meta.csv 
diff ~/jazz/DTL1000/styles-20210503.csv styles.csv 
git commit -a -m "Replaced data files with latest versions"
git push
