FROM python:3

ENV PYTHONUNBUFFERED=1
ENV PATH="/home/printer/.local/bin:$PATH"
RUN useradd -ms /bin/bash -d /home/printer printer
COPY --chown=printer:print requirements.txt /tmp/requirements.txt
USER printer
RUN pip install -r /tmp/requirements.txt gunicorn
COPY --chown=printer:printer . /home/printer
WORKDIR /home/printer
