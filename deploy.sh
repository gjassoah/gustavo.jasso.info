#!/bin/bash

hugo &&
echo "Building tarball..."
tar -C public -cvz . > site.tar.gz &&
echo "Publishing website to sourcehut..."
hut pages publish -d gustavo.jasso.info site.tar.gz
