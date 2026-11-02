FROM nginx:1.27-alpine
# the base image ships its own welcome page; there is to be nothing at the root
RUN rm -f /usr/share/nginx/html/index.html /usr/share/nginx/html/50x.html
COPY default.conf /etc/nginx/conf.d/default.conf
COPY game.html 3b.html android.html ios.html privacy.html support.html tiny-privacy.html tiny-support.html tiny-icon.png icon.png testflight.png 7663a57c94668ec621bbd2abd3736e3d.txt c767ba430051f185a068ec3a9a582c4e.txt starcross-tales.apk /usr/share/nginx/html/
