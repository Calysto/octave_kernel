# Copyright (c) Octave Kernel Development Team.
# Distributed under the terms of the Modified BSD License.
ARG BASE_CONTAINER=quay.io/jupyter/minimal-notebook
FROM $BASE_CONTAINER

LABEL maintainer="Steven Silvester <steven.silvester@ieee.org>"

USER root

# Install octave
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -yq --no-install-recommends octave \
    && rm -rf /var/lib/apt/lists/*

USER $NB_UID

# Install octave_kernel from local source
COPY --chown=$NB_UID:$NB_GID . /tmp/octave_kernel
RUN pip install --no-cache-dir /tmp/octave_kernel \
    && rm -rf /tmp/octave_kernel
