# Use a lightweight Node.js base image
FROM node:20-slim

# Install Python 3 and procps (required for process management in validate.sh)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-minimal \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy package manifests first to leverage Docker cache
COPY package.json ./

# Install dependencies
RUN npm install --omit=dev

# Copy the microservice, tracing wrapper, and simulation scripts
COPY microservice.js tracing.js malware_sim.sh validate.sh ./

# Ensure the simulation and validation scripts are executable
RUN chmod +x malware_sim.sh validate.sh

# Create the data directory required by the microservice
RUN mkdir -p data/db

# Expose the default port for the victim microservice
EXPOSE 3000

# By default, start the victim microservice with OTel pre-require
CMD ["node", "--require", "./tracing.js", "microservice.js"]
