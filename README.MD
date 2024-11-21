# Event Propagator and Consumer Services

This project consists of two main components: an Event Propagator and a Consumer Service. The Event Propagator reads events from a file and sends them to a specified endpoint at regular intervals. The Consumer Service receives these events and stores them in a SQLite database.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/VaiMas/EventHandler.git
    cd EventHandler
    ```

2. Install Poetry if you haven't already:

    ```sh
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. Install the required dependencies:

    ```sh
    make install
    ```

## Usage

To run the Event Propagator and Consumer services, use the following command:

    ```sh
    make run
    ```

## Configuration

The configuration file (`config.json`) is included in the repository and should contain the following fields:

    ```json
    {
        "endpoint": "http://localhost:5000/event",
        "period": 5
    }
    ```

- `endpoint`: The endpoint to which events will be sent.
- `period`: The interval (in seconds) between sending events.

## Running Tests

To run the tests, use the following command:

    ```sh
    make test
    ```

## Project Structure


        EventHandler/
    ├── consumer/
    │   ├── __init__.py
    │   ├── consumer.py
    ├── propagator/
    │   ├── __init__.py
    │   ├── propagator.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_consumer.py
    │   ├── test_propagator.py
    │   ├── test_main.py
    ├── config.json
    ├── events_file.json
    ├── main.py
    ├── pyproject.toml
    ├── README.md
    ├── Makefile
    ├── poetry.lock
