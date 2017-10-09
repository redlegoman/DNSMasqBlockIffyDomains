#!/bin/sh
### Script that appends address records to the DNSMasq.conf file
###

### Script Settings ----------------------------------------------------------- 
BASEDIR="/usr/local/src/DNSMasqBlockIffyDomains" # change this to the directory to cloned to. Or copied to.
GENERATECMD="$BASEDIR/buildListOfDomainsToBlock.py"
MANUALFILE1="$BASEDIR/domainBlacklist.conf"
MANUALFILE2="$BASEDIR/domainWhitelist.conf"
USESCP=0    # set this to a non-zero value if you want this script to copy the output
            # to another server and restart dnsmaq there
REMOTEHOST="10.10.10.6" # the remote server where dnsmasq is actually run

## temp files to use
TMPFILE="$BASEDIR/dnsmasq.blockeddomains.conf"

## Destination folder
CONFIGDIR="/etc/dnsmasq.d/"

## command to reload dnsmasq - change according to your system
## not sure if we need this for dnsmasq
RELOADCMD="/etc/init.d/dnsmasq restart"
#RELOADCMD="/etc/init.d/dnsmasq status"

## check directory for temp files exists - if not, create it (AM)
if [ ! -d $BASEDIR ]
then
    mkdir -p $BASEDIR
fi

## Create manual files if they don't exist
if  [ ! -s $MANUALFILE1 ]
then
    touch $MANUALFILE1
    echo "## Black List Domains" >> $MANUALFILE1
    echo "## ------------------" >> $MANUALFILE1
    echo "## Enter specific websites you want blocking here." >> $MANUALFILE1
    echo "## For example to block images.facebook.com, uncomment the following:" >> $MANUALFILE1
    echo "#### images.facebook.com" >> $MANUALFILE1
    echo "## To block facebook.com and all subdomains, uncomment the following:" >> $MANUALFILE1
    echo "#### facebook.com" >> $MANUALFILE1
    echo "## To block every .com domain (bewarned a lot of key sites are .com), uncomment the follow:" >> $MANUALFILE1
    echo "#### com" >> $MANUALFILE1
fi

## Create manual files if they don't exist
if  [ ! -s $MANUALFILE2 ]
then
    touch $MANUALFILE2
    echo "## White List Domains" >> $MANUALFILE2
    echo "## ------------------" >> $MANUALFILE2
    echo "## ## Enter specific websites you DON'T want blocking here." >> $MANUALFILE2
    echo "## For example to ensure a Googles Ad/Trackers service doesn't get blocked" >> $MANUALFILE2
    echo "## via the Black List Domains uncomment the line below" >> $MANUALFILE2
    echo "#### www.googletagservices.com" >> $MANUALFILE2    
fi

## Call the Python script to generate 'addresses.new'
echo "Generating new blocked address file..."
$GENERATECMD

## check the temp file exists OK before overwriting the existing list
if  [ ! -s $TMPFILE ]
then
	echo "Temp file '$TMPFILE' either doesn't exist or is empty; quitting"
	exit
fi

## Move to the destination folder
if [ $USESCP -ne 0 ] # if we are using a remote dnsmasq host
then
    ## if you are running this script on a different host to the host that dnsmasq is installed on,
    ## scp the files to that remotehost and restart dnsmasq over there. Requires ssh passwordless login.
    scp $TMPFILE root@$REMOTEHOST:/etc/dnsmasq.d/.
    echo "dnsmasq needs to be restarted on $REMOTEHOST to read changes."
    ssh root@$REMOTEHOST ' service dnsmasq restart '
    #ssh root@$REMOTEHOST ' service dnsmasq status '
else 
    cp $TMPFILE $CONFIGDIR
## Restart DNSMasq
    $RELOADCMD
fi


#exit
