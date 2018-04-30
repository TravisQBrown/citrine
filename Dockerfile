FROM python:3.6-slim
WORKDIR /ConvertUnits
ADD . /ConvertUnits
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 5000
ENV NAME CONVERT_UNITS
CMD ["python", "ConvertUnits.py"]