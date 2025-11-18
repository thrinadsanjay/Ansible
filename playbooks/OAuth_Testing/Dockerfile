FROM python:3.11.14

RUN apt-get update && \
    apt-get install -y ca-certificates && \
    rm -rf /var/lib/apt/lists/*

#RUN pip install authlib python-multipart jinja2 itsdangerous python-keycloak[openid] python-jose fastapi uvicorn fastapi-sessions requests --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
RUN pip install gunicorn certifi Flask Authlib Flask-Session requests  python-certifi-win32 pip-system-certs --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

# Install system CA (optional but fine)
COPY ./masupdown/certs/keycloak.pem /etc/ssl/certs/keycloak.crt
RUN update-ca-certificates

# Add CA to certifi trust store (THIS is what Python uses)
# RUN python - <<EOF
# import certifi
# import shutil
# import os

# cafile = certifi.where()
# with open('/tmp/rootCA.crt', 'w') as f:
#     f.write(open('/usr/local/share/ca-certificates/rootCA.crt').read())

# with open(cafile, 'ab') as f:
#     f.write(open('/usr/local/share/ca-certificates/rootCA.crt', 'rb').read())
# EOF

WORKDIR /app

#CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]