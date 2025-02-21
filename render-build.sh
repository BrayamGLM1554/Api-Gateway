#!/bin/bash

# Instalar dependencias necesarias para ODBC y SQL Server
apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    unixodbc \
    unixodbc-dev \
    libssl-dev

# Agregar clave de Microsoft para ODBC
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Instalar ODBC Driver 17 para SQL Server
apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17
