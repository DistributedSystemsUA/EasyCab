# Validation server instructions
IS_TAXI_ID_OK = 0x01
TAXI_ID_OK = 0x06
TAXI_ID_NOT_OK = 0x15

# Kafka server network instructions
NEW_TAXI = 0x01                             # (id, x, y, client_id)
NEW_CLIENT = 0x02                           # (id, x, y)
NEW_LOCATIONS = 0x03                        # (N, (id, x, y), ...)
TAXI_ASSIGNATION = 0x04                     # (taxi_id, client_id)
REQ_LOC = 0x05                              # (client_id, loc_id)
TAXI_MOVE = 0x06                            # (id, mount_client_id, x, y)
TAKE_CLIENT = 0x07                          # (taxi_id, client_id)
TAXI_DISCONNECTED = 0x08                    # (id, current_client_id)
CLIENT_DISCONNECTED = 0X09                  # (id)
CENTRAL_DISCONNECTED = 0x0a                 # ()
TAXI_REDIRECTED = 0x0b                      # (id, x, y, dst_x, dst_y)
REQUEST_MAP_INFO = 0x0c                     # ()
SENSOR_INCONVENIENCE = 0x0d                 # (id)
WHO_IS = 0x0e                               # (id)
