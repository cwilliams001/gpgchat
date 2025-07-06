# gpgchat-modernized

A modernized, user-friendly version of the classic `gpgchat` application. This fork provides a simple, end-to-end encrypted chat service using PGP, with a focus on ease of use and a streamlined setup process.

## Features

*   **End-to-End Encryption:** Messages are encrypted using your local GPG installation, ensuring privacy.
*   **Interactive Client:** A single, interactive client for both sending and receiving messages.
*   **Configuration Wizard:** A simple script to guide you through creating a GPG key and a configuration file.
*   **Docker Support:** Run the client and server in isolated Docker containers.
*   **Python 3:** The entire codebase has been migrated to Python 3.

## Getting Started

This guide will walk you through setting up and using `gpgchat` for the first time.

### 1. Installation

First, you need to install the necessary dependencies.

*   **On Ubuntu/Debian:**
    ```bash
    sudo apt-get update
    sudo apt-get install libzmq-dev gnupg-agent
    ```
*   **On macOS (using [Homebrew](https://brew.sh/)):**
    ```bash
    brew install zeromq
    ```
    You will also need to install [GPG Suite](https://gpgtools.org/).

Then, install the Python dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configuration

Next, run the configuration wizard to create your GPG key and configuration file.

```bash
python3 configure.py
```

The wizard will ask if you want to create a new GPG key or use an existing one. If you're new to GPG, it's recommended to let the script create a key for you. It will also prompt you for a filename for your configuration (e.g., `my_config.py`).

### 3. Running the Server

The server relays messages between clients. You'll need to run it on a machine that is accessible to all users.

```bash
python3 server.py --config my_config.py
```

### 4. Running the Client

Now you can run the client to start chatting.

```bash
python3 client.py --config my_config.py
```

You can now send multiline messages. To send a message, press `Ctrl+D` on a new line.

## Docker Usage

If you have Docker installed, you can run the client and server in containers.

1.  **Build the Docker Image:**
    ```bash
    docker build -t gpgchat .
    ```

2.  **Run the Server:**
    ```bash
    docker run -it --rm -p 8387:8387 --name gpgchat-server gpgchat python3 server.py --config your_config.py
    ```

3.  **Run the Client:**
    To run the client in a container, you need to mount your local GPG directory so it can access your keys.
    ```bash
    docker run -it --rm --name gpgchat-client -v ~/.gnupg:/root/.gnupg gpgchat python3 client.py --config your_config.py
    ```

## How It Works

`gpgchat` uses a central server to relay messages, but all messages are encrypted end-to-end using GPG. This means the server owner cannot read the content of the messages. However, the server does know who is sending messages to whom.
