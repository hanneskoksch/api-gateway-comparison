# Extract tyk binary from official distroless image
FROM tykio/tyk-gateway:v5.10.0 AS tyk-distroless

# Alpine-based runtime with shell and tools
FROM alpine:3.20

# Add tools
RUN apk add --no-cache bash curl ca-certificates libc6-compat

# Create work directory
WORKDIR /opt/tyk-gateway

# Copy binaries and assets from distroless image
COPY --from=tyk-distroless /opt/tyk-gateway /opt/tyk-gateway

# Add tyk binary to PATH
ENV PATH="/opt/tyk-gateway:${PATH}"

# Expose the default Tyk ports
EXPOSE 8080 8081 8082

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["tyk --conf /opt/tyk-gateway/tyk.conf"]

# ENTRYPOINT ["tini", "--", "/opt/tyk-gateway/tyk"]
# CMD ["--conf", "/opt/tyk-gateway/tyk.conf"]

# ENTRYPOINT ["/opt/tyk-gateway/tyk"]
# CMD ["--conf", "/opt/tyk-gateway/tyk.conf"]