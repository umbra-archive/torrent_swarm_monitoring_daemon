import os
import toml

#### TBD
#### add pytdantic validation when toml model is stable

def load_toml_config(custom_config_path=None):
    config_path = custom_config_path or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "config.toml"
    )

    with open(config_path, 'r') as file:
        config = toml.load(file)

    config = apply_base_path(config)
    return config

def apply_base_path(config):
    config["output"]["json_path"] = os.path.join(config["base_path"], config["output"]["json_path"])
    config["output"]["html_path"] = os.path.join(config["base_path"], config["output"]["html_path"])
    config["output"]["stats_path"] = os.path.join(config["base_path"], config["output"]["stats_path"])
    config["output"]["template_dir"] = os.path.join(config["base_path"], config["output"]["template_dir"])
    config["sqlite"]["db_file"] = os.path.join(config["base_path"], config["sqlite"]["db_file"])
    #config["redis"]["rdb_file"] = os.path.join(config["base_path"], config["redis"]["rdb_file"])
    return config


def test():
    print("config file debug")
    print("pase path: ", config["base_path"])
    print("Section: [output]")
    print("    ",config["output"])
    print("Section: [collection]")
    print("    ",config["collection"])
    print("Section: [collection_enabled]")
    print("    ",config["collection_enabled"])
    print("Section: [monitor]")
    print("    ",config["monitor"])
    print("Section: [proxy]")
    print("    ",config["proxy"])


def add_collection_enabled_directive(config):
    collection = config["collection"]
    collection = {k: v for k, v in collection.items() if v.get("enabled", False)}
    config["collection_enabled"] = collection
    return config

config = load_toml_config()
config = add_collection_enabled_directive(config)

if __name__ == "__main__":
    test()
