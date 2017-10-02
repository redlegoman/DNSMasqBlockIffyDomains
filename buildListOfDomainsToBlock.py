#!/usr/bin/env python

""" Python script for downloading domain lists from the web from the following
        http://www.malwaredomains.com
        http://winhelp2002.mvps.org/hosts.htm
        http://pgl.yoyo.org/as/serverlist.php?hostformat=hosts&showintro=1&mimetype=plaintext

    These contain list of dodgy malware, parasitic websites. This script will
    parse this information to produce a DnsMasq Address formated file.

    Also, you can manually specify TLDs and domains to block. Add these to the
    constants file

"""

import urllib
import sys
import os
import argparse
from time import gmtime, strftime

#** Url Target and local destination
mvpsHosts = ['http://winhelp2002.mvps.org/hosts.txt', 'mvpshosts.txt']
malwareDomains = ['http://mirror1.malwaredomains.com/files/domains.txt', 'malwaredomains.txt']
pglYoyoOrg = ['http://pgl.yoyo.org/as/serverlist.php?hostformat=hosts&showintro=1&mimetype=plaintext', 'pglYoyoOrg.txt']
someoneWhoCares = ['http://someonewhocares.org/hosts/hosts', 'someonewhocares.txt']
domainBlacklist = 'domainBlacklist.conf'
domainWhitelist = 'domainWhitelist.conf'

outputFile = 'dnsmasq.blockeddomains.conf'
outputFormat = 'address="/%s/127.0.0.1"\n'

#--------------------------------------------------------------------------------
def reverseString( strng ):
    """ Quick string reverse function - taken from Web """
    return strng[::-1]

#--------------------------------------------------------------------------------
def removePointlessSubdomains( domain, subDomains ):
    for subD in subDomains:
        if( domain[0:len(subD)] == subD):
            domain = domain[len(subD):]
            break

    return domain

def superRemoveDomains( domains ):
    """ Parse domain collection - removing subdomains.
        Sort first, so shortest length domains are first. Split each
        domain on the '.' and build back up to see if already in the collection.
        If there, then this can be ignored as the matched record will take
        precedence and take care of it.
    """
    #** Sort domains, shortest length strings first
    domains.sort(key = lambda s: len(s))
    reducedDomains = []
    for dom in domains:
        match = False
        tlds = dom.split('.')

        for x in range(0, len(tlds)-1):
            #** Build up from 1 to x parts of the domain
            concate = '.'.join(tlds[:x+1])
            if( domains.count(concate) >= 1 ):
                match = True
                break

        if( match == False ):
            #** Switch back to the correct way round
            reducedDomains.append( reverseString( dom ) )

    return reducedDomains

#--------------------------------------------------------------------------------
def listToFile( filename, lst ):
    """ Write out all the parsed domains to a zone file """
    localFile = open(filename, 'w')
    for item in lst:
        localFile.write( outputFormat % item)

    localFile.close()

#--------------------------------------------------------------------------------
def downloadToFile( url, targetFile ):
    """ Copy the contents of a file from a given URL to a local file. """
    print( ' - ' + targetFile )

    try:
        webFile = urllib.urlopen(url)
        localFile = open(targetFile, 'w')
        localFile.write(webFile.read())
        webFile.close()
        localFile.close()
    except Exception, e:
        print(' Errored: ' + e)

#--------------------------------------------------------------------------------
def splitLine( line, elementNo, csvChar ):
    """ Just tries to lift out the element of interest from a CSV string """
    if( csvChar == '' ):
        #** This uses the nice python split on space function
        baseChunks = line.split()
    else:
        baseChunks = line.split( csvChar )

    returnElement = ''
    if( len(baseChunks) > elementNo):
        returnElement = baseChunks[ elementNo ]
        if( returnElement == None ):
            returnElement = ''

    return returnElement

#--------------------------------------------------------------------------------
def parseLine( line, csvChar, elementNo ):
    """ Return the element of interest. Check that there's no comments first. """
    sansComments = splitLine( line, 0, '#' )
    if( sansComments != '' ):
        liftedDomain = splitLine( sansComments, elementNo, csvChar )
    else:
        liftedDomain = ''

    return liftedDomain

#--------------------------------------------------------------------------------
def parseHostsFile( srcFile, csvChar, elementNo ):
    """ Parse the hosts file, strip the IP Address, any unwanted prefix, append to targetFile
        """
    domains = []
    
    """ Remove pointless subdomains from domain. No point having www. or m.,
        just work on higher domain """
    subDomains = ['www.','m.']
    
    if( os.path.isfile(srcFile) ):
        for line in open( srcFile, 'r'):
            newDomain = parseLine( line, csvChar, elementNo )
            newDomain = newDomain.lower()

            #** Check not blank or localhost, never want them
            if( ['','localhost'].count( newDomain ) == 0 ):
                newDomain = removePointlessSubdomains( newDomain, subDomains )
                newDomain = reverseString( newDomain )
                domains.append( newDomain )

    return domains

#--------------------------------------------------------------------------------
def f7(seq):
    """ Very fast remove duplicate from list - taken from StackOverflow """
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

#--------------------------------------------------------------------------------
if __name__ == '__main__':
    print( 'Start: ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()))

    #** Download the latest content
    parser = argparse.ArgumentParser()
    parser.add_argument("-sd", "--skipdownload", action="store_true", default=False)

    args = parser.parse_args()
    if( args.skipdownload == False ):
        print( 'Downloading...' )
        downloadToFile( mvpsHosts[0], mvpsHosts[1] )
        # downloadToFile( malwareDomains[0], malwareDomains[1] )
        downloadToFile( pglYoyoOrg[0], pglYoyoOrg[1] )
        downloadToFile( someoneWhoCares[0], someoneWhoCares[1] )

    #** Create the empty domain list
    domains = []
    safeDomains = []

    #** Populate with our own set of domains, TLDs to block
    domains.extend(parseHostsFile( domainBlacklist, '', 0) )

    #** Populate with downloaded content
    domains.extend( parseHostsFile( mvpsHosts[1], '', 1) )
    # domains.extend( parseHostsFile( malwareDomains[1], '\t', 2)[:] )
    domains.extend( parseHostsFile( pglYoyoOrg[1], '', 1) )
    domains.extend( parseHostsFile( someoneWhoCares[1], '', 1) )

    print( 'Original: ' + str(len(domains)) )
    
    #** Get Safe Domains
    safeDomains.extend( parseHostsFile( domainWhitelist, '', 0) )
    safeTuple = tuple( safeDomains )
    print( 'Good domains: ' +  str(len(safeDomains) ) )
    for domain in domains[:]:
        if domain.startswith(safeTuple):
            print( ' > ' + reverseString(domain) + ' whitelisted')
            domains.remove(domain)
        
    print( 'Original less Good domains: ' + str(len(domains)) )
    newDomains = superRemoveDomains( domains )

    #** Remove duplicates
    f7R = f7( newDomains )
    print( 'Processed: ' + str(len( f7R )) )
    print( 'Duplicate: ' + str( len(domains) - len( f7R ) ) )

    listToFile( outputFile, f7R )

    print( 'End: ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) )
