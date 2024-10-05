# HealthHub Backend API

This project is a FastAPI application serving as the backend API for HealthHub, a comprehensive health management platform. 

- Python 3.8+
- pip (Python package installer)
- OpenAI API key
- Gemini API key
- Cohere API key
- Tavily API key
- Supabase URL and key

## Installation

1. **Clone the repository:**
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Create a virtual environment:**

    ```sh
    python -m venv venv
    ```

3. **Activate the virtual environment:**

    - On Windows:

        ```sh
        venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```sh
        source venv/bin/activate
        ```

4. **Install the dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

## Configuration

1. **Create a `.env` file in the root directory of the project and add the following environment variables:**

    ```dotenv
    OPENAI_API_KEY=<your_openai_api_key>
    GEMINI_API_KEY=<your_gemini_api_key>
    LOCAL_LLM_URL=http://localhost:1234
    GOOGLE_API_KEY=<your_google_api_key>
    COHERE_API_KEY=<your_cohere_api_key>
    TAVILY_API_KEY=<your_tavily_api_key>
    SUPABASE_URL=<your_supabase_url>
    SUPABASE_KEY=<your_supabase_key>
    ```

    Replace the placeholder values with your actual API keys and URLs.

## Running the Application

1. **Start the FastAPI application:**

    ```sh
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

2. **Access the application:**

    Open your web browser and navigate to `http://localhost:8000`.

## Project Structure

- `main.py`: The main entry point of the application.
- `routers/`: Directory containing the different routers for the application.
- `config.py`: Configuration file for the application.
- `requirements.txt`: List of dependencies for the project.
- `.env`: Environment variables for the project.