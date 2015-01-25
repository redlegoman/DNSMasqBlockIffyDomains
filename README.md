# DNSMasqBlockIffyDomains #

Python and Bash script combo.

Simple objective to downloading and parse domain lists from the following websites:
* http://www.malwaredomains.com
* http://winhelp2002.mvps.org/hosts.htm
* http://pgl.yoyo.org

These lovely websites collate lists of dodgy malware, parasitic websites. This *Python* script will download and parse this information to produce a **DnsMasq Address** formatted file that directs all these domains to `127.0.0.1` *(When a web browser receives `127.0.0.1` as the IP address to fetch content from, it's very quickly rejects the connection)*

Also, you can manually specify TLDs and domains to block - add these to the blacklist constants file `domainsBlacklist.conf`
Similarly you can whitelist domains in the file `domainsWhitelist.conf`

The *Bash* script takes this generated **DnsMasq Address** formatted file (`dnsmasq.blockeddomains.conf`) and places it in the standard `/etc/dnsmasq.d` folder to be picked up on service restart. 

## Usage ##
No need to run these scripts more than once a week as updates don't happen on a regular basis, plus we don't want to cause unnecessary costs to these great services

    ./updateDNSMasqConf.sh

**CRON Task** to run every Sunday at midnight:
    sudo crontab -e

    0 0 * * 0 /usr/local/src/DNSMasqBlockIffyDomains/updateDNSMasqConf.sh > /dev/null 2>&1