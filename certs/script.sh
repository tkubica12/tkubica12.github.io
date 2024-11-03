sudo letsencrypt certonly --manual -d tomaskubica.cz


sudo openssl pkcs12 -export -out tomaskubica.pfx -inkey /etc/letsencrypt/live/tomaskubica.cz/privkey.pem -in /etc/letsencrypt/live/tomaskubica.cz/fullchain.pem
