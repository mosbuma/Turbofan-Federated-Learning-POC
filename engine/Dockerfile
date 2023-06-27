FROM heurekalabs/syft-base

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

ENTRYPOINT ["sh", "entrypoint.sh"]
