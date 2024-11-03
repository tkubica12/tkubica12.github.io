echo http://$(ip address show eth0 | grep -w inet | awk '{ print $2 }' | awk -F/ '{ print $1 }'):4000
bundle exec jekyll s --drafts --incremental --host "0.0.0.0"
