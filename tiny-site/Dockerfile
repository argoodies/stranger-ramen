FROM nginx:1.27-alpine
RUN rm -f /usr/share/nginx/html/index.html /usr/share/nginx/html/50x.html
COPY default.conf /etc/nginx/conf.d/default.conf
COPY privacy.html support.html icon.png /usr/share/nginx/html/
