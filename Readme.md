# Torrent Swarm Monitoring Daemon

A Torrent Swarm health Monitoring Daemon (TSMD) for large collections of torrents.

TSMD aims to enable the coordination of effective [seeding](https://en.wikipedia.org/wiki/Seeding_(computing)) of large data corpuses.
By compiling health statistics, torrents most in need of new seeders can be identified.
The individual torrent collections can consist of many thousands of individual torrents.

## Architecture
- The application comprises multiple modules
- Each module can be run independently
- A SQLite database is used for persistence
- (currently not in use) Redis is employed temporarily for deduplicating peer information from various sources

## Features
- Monitors and updates multiple torrent collections.
- Gathers torrent health statistics through DHT peer discovery.
- Acquires torrent health data from trackers using UDP.
- Produces readable torretn health information for both humans (html) and machines (json).

### Collections
Torrent collections are defined by a name and a URL that links to the individual torrents.

### Configuration
Configuration can be done via `config.toml` or command-line arguments.

### Health Assessment
The health of torrents is assessed using DHT and UDP tracker queries.

### Output
Output is generated in HTML and JSON formats. The JSON output is compatible with [libgen-seedtools](https://github.com/subdavis/libgen-seedtools).

## Limitations
#### Security Features
Some client-side security features are not implemented. For more details, see the [security section](.#security).

#### DHT Lookup
- Performing more than 50-30 simultaneous DHT infohash lookups may result in empty results. The cause is being investigated.

#### Tracker Scraper
- The program does not currently support tracker failover.

## Security
Running this server implies a certain level of trust in the website defining the collection. (see config)  This includes:
- Vulnerability to blind GET SSRF, which should be mitigated at the network level.

### Future Improvements
- Implement an HTTP proxy feature for crawling to mitigate SSRF.
- Add more tests.
- Introduce UDP tracker failover and multiple tracker support.
- Enhance concurrency limits in AIODHT library.
- Incorporate better SSRF protection.
- Add capabilities for web torrent and web DHT.
- Explore alternative peer discovery methods.

## Installation

### From GitHub
```bash
git clone [...].git
cd torrent_swarm_monitoring_daemon
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

### Via Pip from GitHub
TBD

### Via Pip from PyPI
No PyPI package available currently.

## Usage
Activate the virtual environment and run the main script:
```bash
source ./venv/bin/activate
python main.py
```

### Running Individual Modules
Activate the virtual environment and run the desired module (see `src` for arguments):
```bash
source ./venv/bin/activate
python -m tsmd.module_name [optional args]
```
Replace `module_name` with the specific module you wish to run, such as `torrent_file_sync`, `dht_swarm_monitor`, `udp_tracker_swarm_monitor`, or `output_generator`.

## Author
- Email: TTBBDD
- GitHub: [@umbra-archive](https://github.com/umbra-archive/)

## License
This project is licensed under the terms of the MIT license.
