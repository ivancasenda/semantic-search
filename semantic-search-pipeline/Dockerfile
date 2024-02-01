FROM tensorflow/tfx:1.13.0

WORKDIR /pipeline
COPY ./ ./

RUN apt update
RUN apt install python3.8-venv -y

RUN pip install -r pipeline_requirements.txt

ENV PYTHONPATH="/pipeline:${PYTHONPATH}"

ENTRYPOINT ["/opt/apache/beam/boot"]