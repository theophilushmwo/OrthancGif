FROM osimis/orthanc
COPY python /python/

RUN pip3 install -r /python/requirements.txt
