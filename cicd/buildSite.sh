#!/bin/bash

# Clone site repo
git clone https://$gitUser:$gitPassword@$gitRepo

# Build site
cd /tomaskubica.cz
bundle install
bundle exec jekyll build
cd /_site

# Upload site
container='$web'

## Upload everything except images and overwrite if exists
for item in $(ls -1)
do
    if [ $item != images ]
    then
        /azcopy cp "./$item" "https://$storageAccount.blob.core.windows.net/$container$sas" --recursive=true --fromTo localBlob
    fi
done

## Upload images and do not overwrite if exists
/azcopy cp "./images/" "https://$storageAccount.blob.core.windows.net/$container$sas" --recursive=true --fromTo localBlob --overwrite=false


