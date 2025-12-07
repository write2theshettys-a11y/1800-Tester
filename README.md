# Twilio Number Tester

This project is a web application that allows users to upload a CSV file of phone numbers and test their status using Twilio's Lookup API. The results are displayed in real-time on the web interface.

## Features

- Upload a CSV file containing phone numbers.
- Check the status of phone numbers (e.g., Active, Inactive, or Twilio Disabled).
- Real-time updates of results using polling.
- Download a sample CSV file for testing.

## Prerequisites

- Python 3.11 or higher
- A Twilio account with API credentials
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd number_tester_twilio
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root or export the variables:
   ```sh
   export TWILIO_ACCOUNT_SID=your_account_sid
   export TWILIO_AUTH_TOKEN=your_auth_token
   ```

## Usage

1. Run the application:
   ```sh
   uvicorn main:app --reload
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

## Docker Deployment

1. Build the Docker image:
   ```sh
   docker build -t number-tester .
   ```

2. Run the Docker container:
   ```sh
   docker run -p 8000:8000 --env-file .env number-tester
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

