#!/bin/bash

curl --create-dirs -o sencha_install/sencha-cmd.run.zip http://cdn.sencha.com/cmd/6.2.1/no-jre/SenchaCmd-6.2.1-linux-amd64.sh.zip
unzip -p sencha_install/sencha-cmd.run.zip > sencha_install/sencha-cmd.run

# Install Sencha Cmd
# To install without user interaction remove "--mode text" and replace by "--mode unattended --prefix /usr/bin/Sencha/Cmd/6.2.1.29"
chmod +x sencha_install/sencha-cmd.run
./sencha_install/sencha-cmd.run -q -dir "/home/pimp/bin/Sencha/Cmd/6.2.1.29"
rm -r sencha_install
