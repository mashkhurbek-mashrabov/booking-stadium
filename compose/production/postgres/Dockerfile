#FROM postgres:15.1-alpine
#FROM postgres:15.3-alpine3.18
#FROM postgres:15.4-bullseye
FROM postgres:15.4-alpine3.18

COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/* &&\
    mv /usr/local/bin/maintenance/* /usr/local/bin &&\
    rmdir /usr/local/bin/maintenance

