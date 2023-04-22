FROM python:3.11.3-slim

# install git
RUN apt update && apt install -y git

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the code
COPY main.py .

CMD ["python", "main.py"]