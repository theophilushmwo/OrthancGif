FROM osimis/orthanc
COPY mip_generator.py /python/
COPY requirements.txt /python/

RUN pip3 install -r /python/requirements.txt
