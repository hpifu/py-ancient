FROM daocloud.io/centos:7

# Install Python 3.6
RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm && \
    yum -y install python36u \
                   python36u-pip \
                   python36u-devel \
    # clean up cache
    && yum -y clean all

# App home
RUN mkdir -p /app/conf
WORKDIR /app
ADD conf/logging.conf /app/conf/
ADD ancient_request.py /app/
RUN pip3.6 install redis
RUN pip3.6 install requests
CMD ["python3.6","/app/ancient_request.py"]