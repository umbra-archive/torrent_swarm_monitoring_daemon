import sys
import bencode
import humanize
import hashlib


"""
pip freeze | grep -i ben
bencode.py==4.0.0

% python old_torrent_file_decoder.py sample.torrent
First level Keys:  odict_keys(['announce', 'creation date', 'info'])
creation_date:          1327049827
comment:                N/A
comment.utf-8:          N/A
created by:             N/A
size (calculated):      20
size (human):           20 Bytes
infohash (calculated):  d0d14c926e6e99761a2fdcff27b403d96376eff6

% python old_torrent_file_decoder.py archlinux-2024.01.01-x86_64.iso.torrent
First level Keys:  odict_keys(['comment', 'created by', 'creation date', 'info', 'url-list'])
creation_date:          1704127703
comment:                Arch Linux 2024.01.01 <https://archlinux.org>
comment.utf-8:          N/A
created by:             mktorrent 1.1
size (calculated):      926232576
size (human):           883.3 MiB
infohash (calculated):  1447bb03de993e1ee7e430526ff1fbac0daf7b44
"""


def calculate_size(info):
    if b'files' in info:
        # multi-file torrent
        return sum(file['length'] for file in info['files'])
    else:
        return info['length']

def calculate_infohash(info):
    return hashlib.sha1(bencode.bencode(info)).hexdigest()

def decode_torrent_file(file_path):
    with open(file_path, 'rb') as file:
        torrent_data = file.read()
        decoded_data = bencode.bdecode(torrent_data)
        print("First level Keys: ", decoded_data.keys())

        info = decoded_data['info']

        try:
            creation_date = decoded_data['creation date']
        except:
            creation_date = "N/A"

        try:
            comment = decoded_data['comment']
        except KeyError:
            comment = "N/A"

        try:
            comment_utf_8 = decoded_data['comment.utf-8']
        except KeyError:
            comment_utf_8 = "N/A"

        try:
            created_by = decoded_data['created by']
        except KeyError:
            created_by = "N/A"

        size = calculate_size(info)
        size_human = humanize.naturalsize(size, binary=True)
        infohash = calculate_infohash(info)

        print(f"creation_date:          {creation_date}")
        print(f"comment:                {comment}")
        print(f"comment.utf-8:          {comment_utf_8}")
        print(f"created by:             {created_by}")
        print(f"size (calculated):      {size}")
        print(f"size (human):           {size_human}")
        print(f"infohash (calculated):  {infohash}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python torrent_file_decoder.py <torrent_file>")
        sys.exit()
    decode_torrent_file(sys.argv[1])
