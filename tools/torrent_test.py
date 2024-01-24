import base64
from torrent import Torrent

# https://sample-file.bazadanni.com/download/applications/torrent/sample.torrent
sample_torrent_base = """ZDg6YW5ub3VuY2UzNTp1ZHA6Ly90cmFja2VyLm9wZW5iaXR0b3JyZW50LmNvbTo4MDEzOmNyZWF0
aW9uIGRhdGVpMTMyNzA0OTgyN2U0OmluZm9kNjpsZW5ndGhpMjBlNDpuYW1lMTA6c2FtcGxlLnR4
dDEyOnBpZWNlIGxlbmd0aGk2NTUzNmU2OnBpZWNlczIwOlzF5lK+DebyeAWzBGT/mwD0ifDJNzpw
cml2YXRlaTFlZWU="""

#sample_torrent_str = base64.b64decode(sample_torrent_base).decode('utf-8')
sample_torrent_bytes = base64.b64decode(sample_torrent_base)

sample_torrent = Torrent(sample_torrent_bytes)

### according to https://www.tools4noobs.com/ the info hash of sample.torrent should be:
### d0d14c926e6e99761a2fdcff27b403d96376eff6
###
sample_torrent.print_info()
