#rm torrentFile.db || true
##rm ../dump.rdb || true
#redis-cli FLUSHALL
#
#rm ../out/torrents.html
#rm ../out/torrents.json


source venv/bin/activate
python -m tsmd.torrent_file_sync
python -m tsmd.dht_swarm_monitor
python -m tsmd.udp_tracker_swarm_monitor
python -m tsmd.output_generator
