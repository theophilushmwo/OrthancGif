FROM osimis/orthanc
COPY mip_generator.py /python/

RUN pip3 install imageio
RUN pip3 install numpy
RUN pip3 install requests
RUN pip3 install scipy