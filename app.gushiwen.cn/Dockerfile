FROM daocloud.io/centos:7

# Install Python 3.6
RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm && \
    yum -y install python36u \
                   python36u-pip \
                   python36u-devel \
    # clean up cache
    && yum -y clean all

# App home
RUN mkdir -p /app/
WORKDIR /app
ADD logging.conf /app/
ADD authors.py /app/
RUN pip3.6 install redis
RUN pip3.6 install requests
CMD ["python3.6","/app/authors.py"]