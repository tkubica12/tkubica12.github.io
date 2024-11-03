# Agent preparation
apt update && apt install ruby-full build-essential zlib1g-dev git -y
gem install jekyll bundler jekyll-feed jekyll-sitemap jekyll-paginate-v2 jekyll-tagging

export gitUser=tomaskubica.cz
export gitPassword=pwbok7j7r5gtrmacogxinbo6b6flipyguoa5n27w2l7uhmj4opxq
export gitRepo="mujtym.visualstudio.com/tomaskubica.cz/_git/tomaskubica.cz"
export storageAccount=tomaskubicatest
export sas="?sp=rwdl&st=2018-12-19T11:14:00Z&se=2028-12-23T11:14:00Z&sv=2018-03-28&sig=qAevRGCn77UoRNhLHn531nJHIOsXmC21aPnRYFcbOUs%3D&sr=c"

git clone https://$gitUser:$gitPassword@$gitRepo
cd /tomaskubica.cz
bundle install
bundle exec jekyll build -d /_site