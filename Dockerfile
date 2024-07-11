FROM ubuntu

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3.12-venv

COPY backend /home/app/
WORKDIR /home/app

RUN ls -R /home/app

RUN python3 -m venv venv

RUN /bin/bash -c "source venv/bin/activate && pip install -r requirements.txt"

EXPOSE 5000

CMD ["venv/bin/python", "run.py"]