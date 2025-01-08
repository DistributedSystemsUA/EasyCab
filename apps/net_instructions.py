# Validation server instructions
IS_TAXI_ID_OK = 0x01
TAXI_ID_OK = 0x06
TAXI_ID_NOT_OK = 0x15

# Kafka server network instructions
NEW_TAXI = 0x01                             # (id, x, y)
NEW_CLIENT = 0x02                           # (id, x, y)
NEW_LOCATION = 0x03                         # (id, x, y)
TAXI_ASSIGNED_TO_CLIENT = 0x04              # (taxi_id, client_id)
CLIENT_REQUEST_LOCATION = 0x05              # (client_id, loc_id)
TAXI_DISCONNECTED = 0x06                    # (id, current_client_id)
REQUEST_MAP_INFO = 0x07                     # ()
TAXI_MOVE = 0x08                            # (id, current_client_id, x, y)
TAXI_REDIRECTED = 0x09                      # (id, client_id, x, y, dst_x, dst_y)
ENTITY_RELOCATION = 0x0a                    # (id, old_x, old_y, x, y)
SENSOR_INCONVENIENCE = 0x0b                 # (id)
WHO_IS = 0x0c                               # (id)
