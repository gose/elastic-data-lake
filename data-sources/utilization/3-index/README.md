# Elasticsearch Settings

Run the following commands in Dev Tools inside Kibana.

### Index Lifecycle Management (ILM) Policy

```
PUT _ilm/policy/utilization
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_size": "50gb"
          }
        }
      }
    }
  }
}
```

### Index Template

We use a `strict` mapping.  Any changes requires re-indexing from the Data Lake.

```
PUT _index_template/utilization
{
  "template": {
    "settings": {
      "index": {
        "lifecycle": {
          "name": "utilization",
          "rollover_alias": "utilization"
        },
        "number_of_replicas": "1"
      }
    },
    "aliases": {
      "utilization": {
        "is_write_index": true
      }
    },
    "mappings": {
      "dynamic": "strict",
      "properties": {
        "input": {
          "properties": {
            "type": {
              "type": "keyword"
            }
          }
        },
        "agent": {
          "properties": {
            "hostname": {
              "type": "keyword",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            },
            "name": {
              "type": "keyword",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            },
            "id": {
              "type": "keyword"
            },
            "ephemeral_id": {
              "type": "keyword"
            },
            "type": {
              "type": "keyword"
            },
            "version": {
              "type": "keyword"
            }
          }
        },
        "@timestamp": {
          "type": "date"
        },
        "ecs": {
          "properties": {
            "version": {
              "type": "keyword"
            }
          }
        },
        "log": {
          "properties": {
            "file": {
              "properties": {
                "path": {
                  "type": "keyword"
                }
              }
            },
            "offset": {
              "type": "integer"
            }
          }
        },
        "host": {
          "properties": {
            "name": {
              "type": "keyword",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            }
          }
        },
        "utilization": {
          "properties": {
            "summary": {
              "properties": {
                "system-used-pct": {
                  "type": "float"
                },
                "cpu-free-pct": {
                  "type": "float"
                },
                "memory-free-pct": {
                  "type": "float"
                },
                "memory-used-pct": {
                  "type": "float"
                },
                "cpu-used-pct": {
                  "type": "float"
                },
                "system-free-pct": {
                  "type": "float"
                }
              }
            },
            "memory": {
              "properties": {
                "cached-gb": {
                  "type": "float"
                },
                "cached-kb": {
                  "type": "integer"
                },
                "available-gb": {
                  "type": "float"
                },
                "swap-free-kb": {
                  "type": "integer"
                },
                "swap-total-gb": {
                  "type": "float"
                },
                "active-gb": {
                  "type": "float"
                },
                "available-kb": {
                  "type": "integer"
                },
                "swap-total-kb": {
                  "type": "integer"
                },
                "active-kb": {
                  "type": "integer"
                },
                "inactive-kb": {
                  "type": "integer"
                },
                "total-gb": {
                  "type": "float"
                },
                "swap-free-gb": {
                  "type": "float"
                },
                "inactive-gb": {
                  "type": "float"
                },
                "total-kb": {
                  "type": "integer"
                },
                "free-kb": {
                  "type": "integer"
                },
                "free-gb": {
                  "type": "float"
                }
              }
            },
            "set": {
              "properties": {
                "name": {
                  "type": "keyword"
                }
              }
            },
            "system": {
              "properties": {
                "serial-number": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "product-name": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "uuid": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "version": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "manufacturer": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                }
              }
            },
            "bios": {
              "properties": {
                "release-date": {
                  "format": "MM/dd/yyyy",
                  "type": "date"
                },
                "vendor": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "version": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                }
              }
            },
            "baseboard": {
              "properties": {
                "serial-number": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "asset-tag": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "product-name": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "version": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "manufacturer": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                }
              }
            },
            "temperature": {
              "properties": {
                "package-id-0-f": {
                  "type": "float"
                },
                "package-id-1-f": {
                  "type": "float"
                },
                "package-id-1-c": {
                  "type": "float"
                },
                "package-id-0-c": {
                  "type": "float"
                }
              }
            },
            "cpu": {
              "properties": {
                "vendor-id": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "l3-cache-kb": {
                  "type": "integer"
                },
                "flags": {
                  "type": "keyword"
                },
                "l1d-cache-kb": {
                  "type": "integer"
                },
                "steal-pct": {
                  "type": "float"
                },
                "stepping": {
                  "type": "integer"
                },
                "bogomips": {
                  "type": "float"
                },
                "guest-pct": {
                  "type": "float"
                },
                "idle-pct": {
                  "type": "float"
                },
                "gnice-pct": {
                  "type": "float"
                },
                "threads-per-core": {
                  "type": "integer"
                },
                "model": {
                  "type": "integer"
                },
                "model-name": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "sockets": {
                  "type": "integer"
                },
                "min-mhz": {
                  "type": "float"
                },
                "hyperthreaded": {
                  "type": "boolean"
                },
                "op-modes": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "architecture": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "virtualization": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "byte-order": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "max-mhz": {
                  "type": "float"
                },
                "l2-cache-kb": {
                  "type": "integer"
                },
                "l1i-cache-kb": {
                  "type": "integer"
                },
                "vcpus": {
                  "type": "integer"
                },
                "sys-pct": {
                  "type": "float"
                },
                "total-cores": {
                  "type": "integer"
                },
                "cores-per-socket": {
                  "type": "integer"
                },
                "nice-pct": {
                  "type": "float"
                },
                "iowait-pct": {
                  "type": "float"
                },
                "virtualization-type": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "irq-pct": {
                  "type": "float"
                },
                "usr-pct": {
                  "type": "float"
                },
                "family": {
                  "type": "integer"
                },
                "hypervisor-vendor": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "mhz": {
                  "type": "float"
                },
                "soft-pct": {
                  "type": "float"
                }
              }
            },
            "chassis": {
              "properties": {
                "serial-number": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "asset-tag": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "type": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "version": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "manufacturer": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                }
              }
            },
            "power": {
              "properties": {
                "volts": {
                  "type": "float"
                },
                "amps": {
                  "type": "float"
                },
                "watts": {
                  "type": "float"
                }
              }
            },
            "loadavg": {
              "properties": {
                "processes": {
                  "properties": {
                    "running": {
                      "type": "integer"
                    },
                    "total": {
                      "type": "integer"
                    }
                  }
                },
                "5m": {
                  "type": "float"
                },
                "15m": {
                  "type": "float"
                },
                "1m": {
                  "type": "float"
                }
              }
            },
            "processor": {
              "properties": {
                "family": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "version": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "frequency": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "manufacturer": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  "index_patterns": [
    "utilization-*"
  ],
  "composed_of": []
}
```
