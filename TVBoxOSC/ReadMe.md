#Rob Yang web:
1. php https://RobYang.serv00.net
2. ~~php http://RobYang.clouds.tw ---OR--- http://RobYang.22web.org/  (need to use browser and turn on javascript http://cpanel.clouds.tw/)
3. ~~php http://RobYang.000.pe (need to use browser and turn on javascript https://dash.infinityfree.com/  )
4. ~~dead net https://RobYang.bsite.com/VodLive/sb8ffa
5. net https://www1.RobYang.us.kg/VodLive/sb8ffa (by https://register.us.kg/panel/main , and DNS hosted by cloudflake)
6. net https://RobYang.runasp.net (by monsterasp.net)
7. http://RobYang.rr.nu
   1. from https://www.sitelutions.com/Auth/urldnscc
   2. DNS hosted by https://dnsexit.com/Direct.sv?cmd=userDNSList&tabnum=4
   3. DDNS: https://dnsexit.com/users/dns/dyn/
   4. redirect in https://dnsexit.com 
      1. by alias.redirect.name in CNAME (https://dnsexit.com/Direct.sv?cmd=userDnsTXT&actioncode=13)
      2. and txt in _redirect.robyang.rr.nu "Redirects to http://www1.robyang.us.kg/VodLive/sb8ffa"
8. http://RobYang.AsSexyAs.com
   1.  from sitelutions
   2.  DNS by https://www.cloudns.net/ free URL forwarding, free 1 DNS hosting
9.  http://2487.rr.nu (by sitelutions, https://www.cloudns.net/ free URL forwarding, free 1 DNS hosting)
   1.  from sitelutions
   2.  DNS by https://www.cloudns.net/ free URL forwarding, free 1 DNS hosting
10. http://RobYang.line.pm (by DNSExit, and DNS hosted by https://dnsexit.com/) (SSL needs to renew every 90 days by login or CURL)


#monitoring 
1. https://robyang.grafana.net/ (monitor web use "Testing & synthetics" > "synthetics")
2. https://app.squaredup.com/
3. ClouDNS (free account with only 1)


#Domain Name:
1. new subdomain name: https:/NIC.us.kg
2. new subdomain name: https://nic.eu.org/
3. new subdomain name: https://www.sitelutions.com/signup 
4. URL redirect: https://redirect.name
   1. github            IN  CNAME  alias.redirect.name
   2. _redirect.github  IN  TXT    "Redirects to http://www1.robyang.us.kg/VodLive/sb8ffa" 
5. Url redirect: https://freedirector.io/dashboard  (free 5 redirect)
6. DNS manage: https://www.cloudflare.com (cannot do rr.nu)
7. DNS manage & DDNS: https://freedns.afraid.org (free URL forwarding)
8. DNS manage & DDNS: https://www.cloudns.net (free URL forwarding, free 1 DNS hosting)
9. DNS manage & DDNS: https://www.changeip.com ($9/year for DNS manage)
10. DNS manage & DDNS: https://dnsexit.com/ (free DNS manage, but only 7 days url forwarding)
   1. Https SSL expires every 90 days
      1. https://dnsexit.com/dns/ssl-api/#renew-domain-ssl
      ```
      curl -H "Content-Type: application/json" --data @/abc/update.json https://api.dnsexit.com/dns/lse.jsp
      ```
      ```
       {
         "apikey": "your-api-key",
         "domain": "robyang.rr.nu",
         "action": "renew",
         "verbose": "true"    // "false"  or "true", when "true", you will see the progress of renewing the SSL. The renew process may take a few minutes
      }
      ```
   2. for DDNS to get API: 
      1. go to domain https://dnsexit.com/Direct.sv?cmd=userShowDns&domainname=robyang.rr.nu
      2. "Dynamic IP update" and select the one to update "generate commoand"
      3. copy the API Key out to somewhere like DNSOmatic
   3. URL Forwarding:
      1. "DNS" go to domain, "edit dns"
      2. go to the dashboard "URL Forwarding" eg, https://dnsexit.com/UrlForward.sv?action=new&domainname=robyang.line.pm
      3. setup formwaring there.
11. DNS manage and DDNS: https://dns.he.net/ (won't take gmail and hotmail)
12. DNS manage: DNSPod

#.net host:
1. https://freeasphosting.net can use own domain. (Left side "Add Domain").
2. https://www.monsterasp.net  
   1. free account not allow add new domain name
   2. free account allow enable MSSQL/MySQL Remote Access (select DB, "users and remot", "Enabled" )
   3. free account can have 5 DB (1GB diskk spave, MSSQL, MariaDB, MySQL)
   4. free account can have https every 90 days to enable manually on the web




#php (FreeHosting):
https://serv00.net (OKTV good)
http://clouds.tw (no https, need to turn on Javascript so OKTV won't work)
https://www.infinityfree.com/    (need to use browser and turn on javascript )
https://profreehost.com/     
https://googiehost.com/freephphosting.html                
https://aeonfree.com/ (no ad blocker)
https://www.freehostia.com/ 
https://freehosting.host/ 
https://www.awardspace.com

#What to do when site gone?
1. go to cloudFlare and update forward url to the new site ("Rule" > "Redirect Rules" > "Bulk Redirect Rules")
   1. https://dash.cloudflare.com/2546565fc3a1939a63376c253d51c06e/robyang.us.kg/rules/redirect-rules/bulk-redirects
   2. update all old url to new url
2. update TVBoxOSC/serv00/index.php to the right new URL sources file
3. update source.Json pointing to the new server
4. update jsm.json pointing to the new server
5. upload to github
6. go to the old database, and update "jb8ffa" (jsm) to the new server eg http://RobYang.rr.nu
7. go to the old database, and update "sb8ffa" (source) to the new server eg http://RobYang.rr.nu
8. go to https://dnsexit.com and forward url to the new site (7 days trial)
   1. https://dnsexit.com/UrlForward.sv?action=show&domainname=2487.rr.nu
   2. https://dnsexit.com/UrlForward.sv?action=show&domainname=robyang.rr.nu
9.  create new freesaphosting account, 
   1. Add new host, like "www2.robyang.us.kg"
   2. create a database
   3. restore database from a *.bak file
   4. update visual studio to point the database to the new correct database name
   5. upload publish zip file


#How to update OKTV when site gone to carry history?
1. hold VOD file for long time on setting
2. update url to the new url (label with be changed due to limited chars)
3. refresh with sources.json and the label will updated correctly
4. go to history and everything should stay


#因serv00服务器要求，如果用户帐户在 90 天内未通过 DevilWEB 或 SSH 面板正确登录，则该帐户将自动从系统中删除，并且无法恢复该帐户收集的数据:
https://www.zzzwb.com/2024/07-11-serv00-automation.html
https://www.youtube.com/watch?v=TNB9tcJi_Uo




GitHub:
| Note        |    URL      |
|-------------|-------------|
| Collect all |  https://github.com/blron/blinve |
| col 2 is |    centered   |
| col 3 is | right-aligned |