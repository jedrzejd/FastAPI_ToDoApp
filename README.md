# FastAPI_ToDoApp

A FastAPI-based To-Do application built with Python 3.10.

## Features

- User authentication and registration.
- CRUD operations for to-do tasks.
- Web interface with responsive design.

## Setup

1. **Clone the repository**:

    ```bash
    git clone https://github.com/jedrzejd/FastAPI_ToDoApp.git
    cd ToDoApp
    ```
2. **Set up a virtual environment**:
    
    ```bash
    python3.10 -m venv venv
    source venv/bin/activate
   ```
3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4. **Run the application**:
    ```bash
    uvicorn main:app --reload
    ```
   
    Visit `http://127.0.0.1:8000` in your browser to access the application.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)