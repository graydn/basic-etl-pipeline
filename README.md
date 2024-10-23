# Forex Data Updater

## Description
A Python application to fetch and store currency exchange rates in an SQLite database, updating rates daily at midnight (if left to run continuously).
This is intended to demonstrate an understanding of the tech and processes used and not as a useful application.

## Requirements
- `requests`
- `pandas`
- `python-dotenv`

## Setup
- first clone the repo onto your local machine using `git clone`
- ensure Docker is installed if you wish to use the containerised version
- ensure Python 3.x.x is installed if you wish to use the localised version
- Get a FREE api key from [text](https://currencyfreaks.com/) !

### Local Setup
1. Install required packages:
   ```bash
   pip install requests pandas python-dotenv
   ```
2. Create a `.env` file in the root directory and include your API_KEY:
   ```bash
   API_KEY=YOUR_API_KEY
   ```
3. Run the app
   ```bash
   python3 main.py
   ```

### Docker Setup
To run the application in a Docker container:

1. **Create .env:**
   Create a `.env` file in the root directory and include your API_KEY:
   ```bash
   API_KEY=YOUR_API_KEY
   ```
2. **Build the Docker image:**
   ```bash
   docker build -t forexapp:latest .
   ```
3. **Run the Docker container:**
   ```bash
   docker run -it --rm --name forexapp forexapp:latest
   ```

## Usage (via terminal interface)
- Enter `show` to view all records.
- Enter `update` to manually update rates.
- Enter `exit` to quit the application.

## Database
Data is stored in `forex_data.db`. Currencies are loaded from `currencies.csv`.

## Docker Configuration
### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### requirements.txt
```bash
requests
pandas
python-dotenv
```

### .dockerignore
```bash
*.db
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
