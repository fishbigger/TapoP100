FROM python:3.8-slim
ENV FLASK_ENV=development
ENV FLASK_DEBUG=0
RUN pip3 install flask PyP100==0.0.18
