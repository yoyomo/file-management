FROM node:24-alpine

# Install pnpm globally
RUN npm install -g pnpm

WORKDIR /

# Copy only package files first to install deps
COPY package.json pnpm-lock.yaml ./

# Install project dependencies (this includes vite locally)
RUN pnpm install

# Copy the rest of the frontend source
COPY . .

EXPOSE 3000

# Use the local vite binary via pnpm
CMD ["pnpm", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]