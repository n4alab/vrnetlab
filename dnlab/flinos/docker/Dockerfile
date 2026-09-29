FROM ghcr.io/srl-labs/vrnetlab-base:0.3.0

ARG IMAGE
ARG VERSION
ENV VERSION=$VERSION

COPY $IMAGE /installed.qcow2
COPY *.py /

EXPOSE 22 5000 10000-10099
HEALTHCHECK CMD ["uv", "run", "/healthcheck.py"]
ENTRYPOINT ["uv", "run", "/launch.py"]
