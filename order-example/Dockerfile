FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /out/api ./cmd/api && CGO_ENABLED=0 go build -o /out/shipping-mock ./cmd/shipping-mock

FROM alpine:3.23
RUN apk add --no-cache ca-certificates
COPY --from=build /out/ /usr/local/bin/
USER 65532:65532
EXPOSE 8080 8081
CMD ["api"]
