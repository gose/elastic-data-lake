#!/usr/bin/env python3

import datetime
import json
import os

path = "/mnt/data-lake"

def get_size(start_path = path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

if __name__ == "__main__":

    if os.path.ismount(path):
        # Get size of each directory
        for d in os.listdir(path):
            size_bytes = get_size(path + "/" + d)
            output = { 
                "@timestamp": datetime.datetime.utcnow().isoformat(),
                "directory": d,
                "bytes": size_bytes
            }
            print(json.dumps(output))
            
        # Get total, available, and free space
        statvfs = os.statvfs(path)
        output = { 
            "@timestamp": datetime.datetime.utcnow().isoformat(),
            "total_bytes": statvfs.f_frsize * statvfs.f_blocks,     # Size of filesystem in bytes
            "free_bytes": statvfs.f_frsize * statvfs.f_bfree,       # Free bytes total
            "available_bytes": statvfs.f_frsize * statvfs.f_bavail, # Free bytes for users
            "mounted": True
        }   
        print(json.dumps(output))
    else:
        output = {
            "@timestamp": datetime.datetime.utcnow().isoformat(),
            "mounted": False
        }
        print(json.dumps(output))

