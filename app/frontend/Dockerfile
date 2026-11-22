FROM nginxinc/nginx-unprivileged:stable-alpine

# Copy ShopSphere frontend application
COPY --chown=101:101 index.html /usr/share/nginx/html/index.html

# Configure Nginx reverse proxy
COPY --chown=101:101 nginx.conf /etc/nginx/conf.d/default.conf

# Frontend HTTP port
EXPOSE 8080

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
