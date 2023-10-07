#!/usr/bin/env sh

rm log/*
rm ._*
rm ipx800V4/._*

tar --no-xattrs --no-acls --no-mac-metadata -cf package.tar *.py ipx800V4 log/ homekitrelay.sh requirements.txt \
      config/sample-config.json config/logging.conf

