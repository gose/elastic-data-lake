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
  "index_patterns": [
    "utilization-*"
  ],
  "template": {
    "settings": {
      "index": {
        "number_of_replicas": "1"
      }
    },
    "mappings": {
      "dynamic": "strict",
      "aliases": {
        "utilization": {}
      },
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "agent": {
          "properties": {
            "ephemeral_id": {
              "type": "keyword"
            },
            "hostname": {
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
            "name": {
              "type": "keyword",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            },
            "type": {
              "type": "keyword"
            },
            "version": {
              "type": "keyword"
            }
          }
        },
        "ecs": {
          "properties": {
            "version": {
              "type": "keyword"
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
        "input": {
          "properties": {
            "type": {
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
        "utilization": {
          "properties": {
            "baseboard": {
              "properties": {
                "asset-tag": {
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
                },
                "product-name": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "serial-number": {
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
            "bios": {
              "properties": {
                "release-date": {
                  "type": "date",
                  "format": "MM/dd/yyyy"
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
            "chassis": {
              "properties": {
                "asset-tag": {
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
                },
                "serial-number": {
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
                }
              }
            },
            "cpu": {
              "properties": {
                "architecture": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "bogomips": {
                  "type": "float"
                },
                "byte-order": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "cores-per-socket": {
                  "type": "integer"
                },
                "family": {
                  "type": "integer"
                },
                "flags": {
                  "type": "keyword"
                },
                "gnice-pct": {
                  "type": "float"
                },
                "guest-pct": {
                  "type": "float"
                },
                "hyperthreaded": {
                  "type": "boolean"
                },
                "hypervisor-vendor": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                },
                "idle-pct": {
                  "type": "float"
                },
                "iowait-pct": {
                  "type": "float"
                },
                "irq-pct": {
                  "type": "float"
                },
                "l1d-cache-kb": {
                  "type": "integer"
                },
                "l1i-cache-kb": {
                  "type": "integer"
                },
                "l2-cache-kb": {
                  "type": "integer"
                },
                "l3-cache-kb": {
                  "type": "integer"
                },
                "max-mhz": {
                  "type": "float"
                },
                "mhz": {
                  "type": "float"
                },
                "min-mhz": {
                  "type": "float"
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
                "nice-pct": {
                  "type": "float"
                },
                "op-modes": {
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
                "soft-pct": {
                  "type": "float"
                },
                "steal-pct": {
                  "type": "float"
                },
                "stepping": {
                  "type": "integer"
                },
                "sys-pct": {
                  "type": "float"
                },
                "threads-per-core": {
                  "type": "integer"
                },
                "total-cores": {
                  "type": "integer"
                },
                "usr-pct": {
                  "type": "float"
                },
                "vcpus": {
                  "type": "integer"
                },
                "vendor-id": {
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
                "virtualization-type": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword"
                    }
                  }
                }
              }
            },
            "loadavg": {
              "properties": {
                "15m": {
                  "type": "float"
                },
                "1m": {
                  "type": "float"
                },
                "5m": {
                  "type": "float"
                },
                "processes": {
                  "properties": {
                    "running": {
                      "type": "integer"
                    },
                    "total": {
                      "type": "integer"
                    }
                  }
                }
              }
            },
            "memory": {
              "properties": {
                "active-gb": {
                  "type": "float"
                },
                "active-kb": {
                  "type": "integer"
                },
                "available-gb": {
                  "type": "float"
                },
                "available-kb": {
                  "type": "integer"
                },
                "cached-gb": {
                  "type": "float"
                },
                "cached-kb": {
                  "type": "integer"
                },
                "free-gb": {
                  "type": "float"
                },
                "free-kb": {
                  "type": "integer"
                },
                "inactive-gb": {
                  "type": "float"
                },
                "inactive-kb": {
                  "type": "integer"
                },
                "swap-free-gb": {
                  "type": "float"
                },
                "swap-free-kb": {
                  "type": "integer"
                },
                "swap-total-gb": {
                  "type": "float"
                },
                "swap-total-kb": {
                  "type": "integer"
                },
                "total-gb": {
                  "type": "float"
                },
                "total-kb": {
                  "type": "integer"
                }
              }
            },
            "power": {
              "properties": {
                "amps": {
                  "type": "float"
                },
                "volts": {
                  "type": "float"
                },
                "watts": {
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
            "set": {
              "properties": {
                "name": {
                  "type": "keyword"
                }
              }
            },
            "summary": {
              "properties": {
                "cpu-free-pct": {
                  "type": "float"
                },
                "cpu-used-pct": {
                  "type": "float"
                },
                "memory-free-pct": {
                  "type": "float"
                },
                "memory-used-pct": {
                  "type": "float"
                },
                "system-free-pct": {
                  "type": "float"
                },
                "system-used-pct": {
                  "type": "float"
                }
              }
            },
            "system": {
              "properties": {
                "manufacturer": {
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
                "serial-number": {
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
                }
              }
            },
            "temperature": {
              "properties": {
                "package-id-0-c": {
                  "type": "float"
                },
                "package-id-0-f": {
                  "type": "float"
                },
                "package-id-1-c": {
                  "type": "float"
                },
                "package-id-1-f": {
                  "type": "float"
                }
              }
            }
          }
        }
      }
    }
  }
}
```
