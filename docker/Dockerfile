ARG BASE_IMAGE=
FROM ${BASE_IMAGE}
MAINTAINER Thingpedia Admins <thingpedia-admins@lists.stanford.edu>

USER root
RUN apt update && apt install -y file wget sudo python3 python3-pip curl

RUN curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -

RUN apt install -y nodejs

RUN curl -L "https://storage.googleapis.com/kubernetes-release/release/v1.17.13/bin/linux/amd64/kubectl" -o /usr/local/bin/kubectl && \
   chmod +x /usr/local/bin/kubectl

RUN python3 -m pip install -U pip

RUN pip3 install --use-feature=2020-resolver \
   jupyter jupyterlab jupyterlab-git matplotlib \
   kfp kubeflow-metadata awscli
RUN npm install -g tslab

# add user jovyan (jupyter notebook hardcoded user)
RUN useradd -ms /bin/bash -u 1001 jovyan && id jovyan

RUN adduser jovyan sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN pip3 install torch==1.7.0+cu110 torchvision==0.8.1+cu110 torchaudio===0.7.0 -f https://download.pytorch.org/whl/torch_stable.html
RUN apt upgrade -y
# RUN echo 'y \n y \n' | unminimize
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Pacific
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt install -y git zsh openssh-server

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

RUN pip3 install fvcore numpy simplejson av pyyaml tqdm psutil opencv-python tensorboard moviepy pandas pytorch_lightning pycocotools scipy
RUN git clone https://github.com/stanford-oval/epic-kitchen-lstm.git

RUN apt install -y nano rsync screen
RUN echo "GatewayPorts yes\n" >> /etc/ssh/sshd_config

ENV NB_USER=jovyan
ENV NB_UID=1001
ENV HOME=/home/jovyan
ENV NB_PREFIX /
ENV PATH=$HOME/.local/bin:$HOME/.yarn/bin:$PATH
ENV MINIO_ENDPOINT=minio-service.kubeflow:9000
ENV TZ=America/Pacific
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN python3 -m ipykernel.kernelspec
RUN tslab install --python=python3
RUN jupyter lab build

COPY download-dataset.sh download-pretrained.sh lib.sh sync-repo.sh ./

# Start of custom docker image

# Move to jovyan folder
WORKDIR /home/jovyan
RUN mkdir CURIS

# Install custom code in CURIS directory
WORKDIR /home/jovyan/CURIS
RUN wget https://raw.githubusercontent.com/StanfordHCI/virtualhome/master/docker/init_x11.sh
RUN wget https://gist.githubusercontent.com/valkjsaaa/22616cd8fcaa22d481a492ae9c8f9cf1/raw/16aa0945c868215d2109e91f309b6a7143b2599f/start_x11.sh

RUN source ./init_x11.sh
RUN source ./start_x11.sh
RUN mkdir Output
RUN mkdir Data

# get virtualhome - contains python api
RUN git clone https://github.com/StanfordHCI/virtualhome.git
WORKDIR /home/jovyan/CURIS/virtualhome
RUN python3 -m pip install -r requirements.txt
WORKDIR /home/jovyan/CURIS

# get virtualhome unity executable and data

# make sure unzip is installed
RUN sudo apt install unzip

# setup aws cli
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN sudo ./aws/install

# copy virtualhome_unity build and data
RUN aws s3 cp --recursive s3://geniehai/jackiey/virtualhome/ .
RUN unzip virtualhome_linux_Data.zip

USER root
CMD ["bash"]