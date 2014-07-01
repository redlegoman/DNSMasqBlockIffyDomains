#!/bin/sh
### Script that appends address records to the DNSMasq.conf file
###

## Call the Python script to generate 'addresses.new'
echo "Generating new blocked Address file"
./buildListOfDomainsToBlock.py

configfile=/etc/dnsmasq.conf

## command to reload dnsmasq - change according to your system
## not sure if we need this for dnsmasq
reloadcmd='/etc/init.d/dnsmasq restart'

## temp files to use
tmpfile="addresses.new"
tmpconffile="dnsmasq.conf.$$"

## check the temp file exists OK before overwriting the existing list
if  [ ! -s $tmpfile ]
then
echo "Temp file '$tmpfile' either doesn't exist or is empty; quitting"
exit
fi

## get a fresh list of ad server addresses for dnsmasq to refuse
cat $configfile | grep -v "address=" > $tmpconffile

while read line; do
    echo "${line}" >> $tmpconffile
done < $tmpfile

mv $tmpconffile $configfile
$reloadcmd

exit