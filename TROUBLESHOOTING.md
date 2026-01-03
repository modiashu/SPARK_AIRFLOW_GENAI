# Troubleshooting Guide

## Network/DNS Issues During Installation

### Problem: DNS lookup failures when downloading packages

**Error message:**
```
error: Failed to fetch: `https://files.pythonhosted.org/packages/...`
  Caused by: dns error
  Caused by: failed to lookup address information: nodename nor servname provided, or not known
```

### Solutions

#### 1. Check Network Connectivity
```bash
# Test DNS resolution
ping files.pythonhosted.org

# Test HTTPS connectivity
curl -I https://pypi.org
```

#### 2. Configure DNS Settings (macOS)
```bash
# Use Google DNS or Cloudflare DNS
# System Preferences → Network → Advanced → DNS
# Add: 8.8.8.8, 8.8.4.4, 1.1.1.1
```

#### 3. Configure Corporate Proxy (if applicable)
```bash
# Set proxy environment variables
export HTTP_PROXY="http://proxy.company.com:8080"
export HTTPS_PROXY="http://proxy.company.com:8080"
export NO_PROXY="localhost,127.0.0.1"

# Then run setup again
./scripts/setup.sh
```

#### 4. Use Alternative Installation Method
```bash
# Activate virtual environment
source .venv/bin/activate

# Install using pip with retry logic
pip install --retries 5 --timeout 30 -e .
```

#### 5. Manual Package Installation
If all else fails, install packages one by one:
```bash
source .venv/bin/activate

pip install apache-airflow==2.9.3
pip install apache-airflow-providers-apache-spark==4.10.1
pip install pyspark==3.5.1
pip install pandas==2.2.2
pip install python-dotenv==1.0.1
pip install requests==2.31.0
pip install pytest==8.2.2
pip install pytest-cov==5.0.0
```

#### 6. Offline Installation
Download packages on a machine with internet and install offline:
```bash
# On machine with internet
pip download -d ./packages -r requirements.txt

# Transfer ./packages directory to your machine, then:
pip install --no-index --find-links=./packages -e .
```

## UV Deprecation Warning

### Problem: `tool.uv.dev-dependencies` deprecation warning

**Fixed in version 0.1.0+** - The project now uses `dependency-groups.dev` format.

If you see this warning, pull the latest changes or update [pyproject.toml](pyproject.toml) manually.

## Airflow Database Issues

### Problem: Airflow database initialization fails

```bash
# Reset Airflow database
rm -f airflow.db airflow-webserver.pid

# Reinitialize
export AIRFLOW_HOME=$(pwd)
airflow db reset -y
airflow db init
```

## Spark Job Failures

### Problem: Java not found

```bash
# macOS
brew install openjdk@11
echo 'export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"' >> ~/.zshrc

# Linux
sudo apt-get update
sudo apt-get install openjdk-11-jdk
```

### Problem: JAVA_HOME not set

```bash
# macOS (add to ~/.zshrc or ~/.bash_profile)
export JAVA_HOME=$(/usr/libexec/java_home -v 11)

# Linux (add to ~/.bashrc)
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```

## Permission Issues

### Problem: Scripts not executable

```bash
chmod +x scripts/*.sh
```

## Virtual Environment Issues

### Problem: Virtual environment not activating

```bash
# Remove and recreate
rm -rf .venv
uv venv .venv --python 3.11
source .venv/bin/activate
```

## Port Already in Use

### Problem: Port 8080 already in use

```bash
# Find process using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>

# Or use different port by updating .env
echo "AIRFLOW_WEBSERVER_PORT=8081" >> .env
```

## Getting Help

If you continue experiencing issues:

1. Check the logs in the `logs/` directory
2. Verify all prerequisites are met (see [README.md](README.md))
3. Check network connectivity and DNS resolution
4. Try the manual installation steps above
5. Open an issue with:
   - Full error message
   - Output of `uv --version` or `pip --version`
   - Output of `python --version`
   - Output of `java -version`
   - Your OS and version
