#!/bin/sh
### Script that appends address records to the DNSMasq.conf file
###

### Script Settings ----------------------------------------------------------- 
BASEDIR="/usr/local/src/DNSMasqBlockIffyDomains"
GENERATECMD="$BASEDIR/buildListOfDomainsToBlock.py"

## temp files to use
TMPFILE="$BASEDIR/addresses.new"
TMPCONFFILE="$BASEDIR/dnsmasq.conf.$$"

## command to reload dnsmasq - change according to your system
## not sure if we need this for dnsmasq
RELOADCMD="/etc/init.d/dnsmasq restart"
CONFIGFILE="/etc/dnsmasq.conf"

## Call the Python script to generate 'addresses.new'
echo "Generating new blocked Address file"
$GENERATECMD

## check the temp file exists OK before overwriting the existing list
if  [[ ! -s $TMPFILE ]] ; then
	echo "Temp file '$TMPFILE' either doesn't exist or is empty; quitting"
	exit
fi

## get a fresh list of ad server addresses for dnsmasq to refuse
cat $CONFIGFILE | grep -v "address=" > $TMPCONFFILE

while read line; do
    echo "${line}" >> $TMPCONFFILE
done < $TMPFILE

mv $TMPCONFFILE $CONFIGFILE
$RELOADCMD

exit