FROM osimis/orthanc

RUN pip3 install fpdf
RUN pip3 install imageio
RUN pip3 install matplotlib
RUN pip3 install numpy
RUN pip3 install requests
RUN pip3 install scipy
