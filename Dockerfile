# Copyright (c) Octave Kernel Development Team.
# Distributed under the terms of the Modified BSD License.
ARG BASE_CONTAINER=jupyter/minimal-notebook
FROM $BASE_CONTAINER

LABEL maintainer="Steven Silvester <steven.silvester@ieee.org>"

USER root

# Install octave
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get -yq dist-upgrade \
    && apt-get install -yq --no-install-recommends \
    octave \
    && rm -rf /var/lib/apt/lists/*

USER $NB_UID

# Install extra packages
RUN conda install --quiet --yes \
    'octave_kernel'  && \
    conda clean -tipy && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER


USER $NB_UID
