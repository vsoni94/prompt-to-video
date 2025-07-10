# Stage 1: Build React app
FROM node:18-alpine as build

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy all source files
COPY . .

# Build React app (no env var needed)
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:stable-alpine

# Copy built React files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx config (if you have one)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
