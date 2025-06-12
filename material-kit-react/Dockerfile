# Build stage
FROM node:18 as build

WORKDIR /app
COPY . .
RUN npm install
RUN npm run build

# Production stage
FROM nginx:stable-alpine

# Remove default Nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy build output to Nginx's HTML folder
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx config if you have one (optional)
# COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
