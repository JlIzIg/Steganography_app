FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y libx11-6 libxext-dev libxrender-dev libxinerama-dev  libxi-dev libxrandr-dev libxcursor-dev libxtst-dev tk-dev && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]