import redis
import struct
import socket

from .config_loader import config

redis_client = dict()
for collection_name, collection_val in config["collection"].items():
    redis_client[collection_name] = redis.Redis(host='localhost', port=6379, db=collection_val["redis_db_id"])


# Helper functions to avoid inefficient storage of IPs as strings.
# Additionally, merge port into IP for improved efficiency.
def ip_port_to_int(ip_address, port):
    if not isinstance(port, int):
        raise TypeError("Value 'Port' must be an integer")
    ip_int = struct.unpack("!I", socket.inet_aton(ip_address))[0]
    return (ip_int << 16) | port


def int_to_ip_port(combined_int):
    if not isinstance(combined_int, int):
        raise TypeError("Value 'combined_int' must be an integer")
    port = combined_int & 0xFFFF
    ip_int = combined_int >> 16
    ip_address = socket.inet_ntoa(struct.pack("!I", ip_int))
    return ip_address, port


def test_ip_conversion():
    print("testing ip conversion")
    test_data = [["1.1.1.1"        ,1    , 1103823437825  ],
                 ["10.0.0.1"       ,1024 , 10995116344320 ],
                 ["127.0.0.1"      ,22   , 139637976793110],
                 ["192.168.1.1"    ,50000, 211827803931472],
                 ["255.255.255.255",65535, 281474976710655]]

    for t in test_data:
        ip, port, expected = t
        print(f"testing ip_port_to_int({ip},{port})")
        i = ip_port_to_int(ip, port)
        print(f"  -> {i}")

        print(f"testing int_to_ip_port({i})")
        result_ip, result_port = int_to_ip_port(i)
        print(f"  -> {result_ip} {result_port}")
        if ip == result_ip and port == result_port:
            print("[test passed]")
        else:
            print(f"ERROR: with values {t} -> {result_ip} {result_port}")


def test_redis_config():
    print("testing redis config")
    print(redis_client)


if __name__ == "__main__":
    test_ip_conversion()
    test_redis_config()
