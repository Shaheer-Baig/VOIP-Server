# client.py
import socket
import threading
import pyaudio

# Constants
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12346
BUFF_SIZE = 1024


def audio_stream(sock):
    """Handle real-time audio streaming during a call."""
    audio = pyaudio.PyAudio()

    # Create audio streams
    stream_out = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=BUFF_SIZE)
    stream_in = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=BUFF_SIZE)

    def send_audio():
        while True:
            try:
                data = stream_out.read(BUFF_SIZE, exception_on_overflow=False)
                sock.sendall(data)
            except Exception:
                break

    def receive_audio():
        while True:
            try:
                data = sock.recv(BUFF_SIZE)
                if not data:
                    break
                stream_in.write(data)
            except Exception:
                break

    # Start audio streams in separate threads
    send_thread = threading.Thread(target=send_audio)
    receive_thread = threading.Thread(target=receive_audio)
    send_thread.start()
    receive_thread.start()

    send_thread.join()
    receive_thread.join()

    # Close streams
    stream_out.stop_stream()
    stream_out.close()
    stream_in.stop_stream()
    stream_in.close()
    audio.terminate()


def handle_server_responses(sock):
    """Listen to messages from the server."""
    while True:
        try:
            message = sock.recv(BUFF_SIZE).decode('utf-8')
            if message:
                print(message)
                if "Type \"yes\" to accept" in message:
                    response = input("Your response: ").strip()
                    sock.send(response.encode('utf-8'))
                elif "Call started" in message:
                    print("Call initiated. Streaming audio...")
                    audio_stream(sock)
                    print("Call ended.")
            else:
                break
        except ConnectionResetError:
            print("Disconnected from server.")
            break


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"Connected to server {SERVER_HOST}:{SERVER_PORT}")

    # Start a thread to handle server responses
    threading.Thread(target=handle_server_responses, args=(client_socket,), daemon=True).start()

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() == 'exit':
                client_socket.send(user_input.encode('utf-8'))
                print("Exiting...")
                break
            client_socket.send(user_input.encode('utf-8'))
        except KeyboardInterrupt:
            print("Exiting...")
            client_socket.send(b'exit')
            break
        except ConnectionResetError:
            print("Connection lost.")
            break

    client_socket.close()


if __name__ == '__main__':
    start_client()
