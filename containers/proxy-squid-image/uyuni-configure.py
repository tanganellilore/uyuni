#!/usr/bin/python3

import os
import re
import yaml

docker_subnets = '''
acl all src all
acl docker src 172.16.0.0/12  # RFC1918 possible internal network
acl docker src 192.168.0.0/8  # RFC1918 possible internal network
acl docker src fc00::/7       # RFC 4193 local private network range
acl docker src fe80::/10
'''

# read from file
with open("/etc/uyuni/config.yaml") as source:
    config = yaml.safe_load(source)

    # read to existing config file
    with open("/etc/squid/squid.conf", "r+") as config_file:
        file_content = config_file.read()
        file_content = re.sub(r"cache_dir aufs .*", f"cache_dir aufs /var/cache/squid {str(config['max_cache_size_mb'])} 16 256", file_content)
        file_content = re.sub(r"access_log .*", "access_log stdio:/proc/self/fd/1 squid", file_content)

        if os.getenv("SQUID_HOST", config.get("squid_host", None)):
            # add lines to squid.conf after 'acl all src all'
            file_content = re.sub(r"acl all src all", docker_subnets, file_content)
            file_content = re.sub(r"http_access allow localhost", "http_access allow docker\nhttp_access allow localhost", file_content)
        
        # writing back the content
        config_file.seek(0,0)
        config_file.write(file_content)
        config_file.truncate()

# make sure "squid" is the user and group owner of the cache squid path
os.system('chown -R squid:squid /var/cache/squid')
