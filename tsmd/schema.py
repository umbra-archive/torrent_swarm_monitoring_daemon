from peewee import Model, SqliteDatabase, CharField, BlobField, IntegerField
from .config_loader import config

pragmas_config = config.get("sqlite", {}).get("pragmas", {})


db = SqliteDatabase(
    config["sqlite"]["db_file"],
    timeout=config["sqlite"]["timeout"],
    pragmas=pragmas_config,
)


class BaseModel(Model):
    class Meta:
        database = db


def create_dynamic_table_model(table_name):
    class DynamicTableModel(BaseModel):

        name = CharField()
        content = BlobField(null=True)
        infohash = CharField(max_length=40, null=True)
        src_url = CharField(null=True)
        dht_scraped = IntegerField(null=True)
        dht_peers = IntegerField(null=True)
        tracker_seeder = IntegerField(null=True)
        tracker_leecher = IntegerField(null=True)
        tracker_scraped = IntegerField(null=True)
        tracker_compleeted = IntegerField(null=True)
        size = IntegerField(null=True)

        # fields from .torrent file
        tf_created_by = CharField(null=True)
        tf_creation_date = IntegerField(null=True)
        tf_comment = CharField(null=True)
        tf_comment_utf8 = CharField(null=True)

    DynamicTableModel._meta.table_name = table_name

    return DynamicTableModel
