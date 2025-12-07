# 1800-Tester

This project is a web application that allows users to upload a CSV file of 1-800 phone numbers and test their status using Twilio's Lookup API. The results are displayed in the web interface. 

## Features

- Upload a CSV file containing phone numbers.
- Check the status of phone numbers (e.g., Active, Inactive, or Disabled).
- Real-time updates of results using polling.
- Download the results as a CSV file with timestamp of test completion.

## Prerequisites

- Python 3.11 or higher
- A Twilio account with API credentials
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd 1800-Tester
   ```

2. Install dependencies:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip3 install -r requirements.txt
   ```

3. Set up environment variables:
   Copy the example file and fill in your Twilio credentials:
   ```sh
   cp .env.example .env
   # then edit .env and add your real values
   ```

## Usage

1. Run the application locally:
   ```sh
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000
   ```

3. Upload a CSV file with phone numbers in the first column.

4. View the results in real-time.

## Sample CSV

You can download a sample CSV file from the application or create one manually:
```csv
number
+18005551234
+18001234567
+18005559876
```

## Docker Deployment (optional)

1. Build the Docker image:
   ```sh
   docker build -t 1800-tester .
   ```

2. Run the Docker container:
   ```sh
   docker run -p 8000:8000 --env-file .env 1800-tester
   ```

3. Access the application at:
   ```
   http://127.0.0.1:8000
   ```

## Dependencies

- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [Pandas](https://pandas.pydata.org/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [Twilio](https://www.twilio.com/)

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- [Twilio](https://www.twilio.com/) for providing the Lookup API.
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework.

