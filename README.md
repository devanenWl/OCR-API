# LaTeX OCR

LaTeX OCR is a web application that converts images of equations into LaTeX code. This project uses Python, FastAPI for the backend, Streamlit for the frontend, and Celery for task management. It also involves MongoDB for data storage and Redis for Celery's message broker.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need to have Python installed on your machine. You can download Python [here](https://www.python.org/downloads/).

You also need to install MongoDB and Redis on your local machine or use the provided cloud services in the .env file. 

### Installing

1. Clone the repository
```sh
git clone https://github.com/KenKout/OCR-AI.git
```

2. Navigate to the project directory
```sh
cd OCR-AI
```

3. Install the required packages
```sh
pip install -r requirements.txt
```

4. Run the application
```sh
python run.py
```

The application consists of three parts which run concurrently:

- The FastAPI backend which handles requests
- The Streamlit frontend which provides the user interface
- The Celery worker which processes tasks

## Usage

- Open your browser and navigate to the Streamlit server (usually localhost:8501).
- Upload an image of an equation.
- Click the 'Convert' button to start processing the image.
- The LaTeX code corresponding to the equation in the image will be displayed.

## Built With

- Python
- FastAPI
- Streamlit
- Celery
- MongoDB
- Redis

## Authors

- KenKout

## License

This project is licensed under the MIT License.

## Acknowledgments

- OpenAI for providing the language model
- The FastAPI team for creating a great web framework
- The Streamlit team for creating an easy-to-use way to create beautiful data apps