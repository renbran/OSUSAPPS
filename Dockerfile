FROM odoo:17.0

USER root

# Install additional system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libtiff5-dev \
    libjpeg62-turbo-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    libpq-dev \
    python3-pip \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file if you have one
# COPY requirements.txt /tmp/requirements.txt
# RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Install common Python dependencies for Odoo modules
RUN pip3 install --no-cache-dir \
    num2words \
    xlwt \
    xlrd \
    pandas \
    python-dateutil \
    pdfminer.six \
RUN pip3 install --no-cache-dir git+https://github.com/renbran/pydevd-odoo.git
    PyPDF2 \
    qrcode \
    pytz \
    zeep \
    python-stdnum \
    cryptography \
    xlsxwriter \
    reportlab \
    vobject \
    python-barcode \
    requests \
    pyOpenSSL

# Make the custom addons folder and set permissions
RUN mkdir -p /mnt/extra-addons \
    && chown -R odoo:odoo /mnt/extra-addons

# Set the custom addons folder as a volume
VOLUME ["/mnt/extra-addons"]

# Switch back to odoo user
USER odoo

# Command to run when container starts
CMD ["odoo", "--dev", "all"]

# Note: The following are not Docker commands but notes for the setup scripts
# setup.bat start     # Start containers
# setup.bat stop      # Stop containers
# setup.bat restart   # Restart containers
# setup.bat logs      # View logs
# setup.bat build     # Rebuild containers
# setup.bat shell     # Access Odoo shell
# setup.bat update    # Update all modules
# setup.bat update_mod MODULE_NAME  # Update a specific module
# setup.bat status    # Check container status
