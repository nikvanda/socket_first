import socket


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 1050
    s.bind(('', port))

    s.listen(1)
    conn, addr = s.accept()
    while True:
        data = conn.recv(1024)
        # print(data)
        enc_1, length = data[:2]
        rest_data = data[2:]
        # print(enc_1)
        # print(length)

        if rest_data == b'866897050116377' and len(rest_data) == length:
            conn.send()

    conn.close()
#     b'\x00\x0f866897050116377'


if __name__ == '__main__':
    main()
    # data = b'\x00\x0f866897050116377'
    # enc_1, enc_2 = data[:2]
    # rest_data = data[2:]
    # print(enc_1)
    # print(enc_2)
    # print(rest_data)
    # print(rest_data == data[2:])
