FROM ubuntu

RUN apt update && apt install ruby-full build-essential zlib1g-dev git liblttng-ust0 libcurl3 libicu60 libunwind8 libuuid1 libssl1.0.0 libkrb5-3 rsync -y
RUN gem install jekyll bundler jekyll-feed jekyll-sitemap jekyll-paginate-v2 jekyll-tagging
COPY buildSite.sh azcopy ./
RUN chmod +x /buildSite.sh /azcopy
CMD ["./buildSite.sh"]