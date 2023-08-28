#!/bin/bash

hugo
tar -C public -cvz . > site.tar.gz
hut pages publish -d gustavo.jasso.info site.tar.gz
