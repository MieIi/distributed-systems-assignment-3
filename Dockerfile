FROM python:3
COPY . /wikithingy
WORKDIR /wikithingy
RUN pip install -r req.txt
CMD python3 wikithingy.py