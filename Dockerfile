FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 3000

# set environment variables
ENV WEATHER_API_KEY=665af194074dced099acd8f186177bb9
ENV QUOTE_API_KEY=8XA9HwCe9dSOg3R4DwTuHA==yt3DGw8BwXoODcIR

# Run server.py when the container launches
CMD ["python", "server.py"]