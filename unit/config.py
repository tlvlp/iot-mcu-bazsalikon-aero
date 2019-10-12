import ujson

# Unit - ID
project = "tlvlp.iot.BazsalikON"
name = "aero"
mqtt_unit_id = "{}-{}".format(project, name)
unit_id_dict = {"unitID": mqtt_unit_id, "project": project, "name": name}

# Unit - Hardware
water_temp_sensor_pin = 23
growlight_pin = 32
growlight_relay_active_at = 1
growlight_persistence_path = "growlight_status"
irrigation_pin = 33
irrigation_relay_active_at = 1
irrigation_on_sec = 120
irrigation_off_sec = 120

# Unit - Scheduling
gc_collect_interval_sec = 1700
post_status_interval_sec = 600

# WIFI
wifi_ssid = "PLACEHOLDER"
wifi_password = "PLACEHOLDER"
wifi_connection_check_interval_sec = 1
wifi_ip = "PLACEHOLDER"

# MQTT
mqtt_connection_check_interval_sec = 1
mqtt_message_check_interval_ms = 100
mqtt_keepalive_sec = 200
mqtt_qos = 1
mqtt_use_ssl = True
mqtt_queue_size = 10
mqtt_checkout_payload = ujson.dumps(unit_id_dict)

# MQTT - Credentials
mqtt_server = "PLACEHOLDER"
mqtt_port = "PLACEHOLDER"
mqtt_user = "PLACEHOLDER"
mqtt_password = "PLACEHOLDER"

# MQTT - topics
mqtt_topic_status_request = "/global/status_request"
mqtt_topic_status = "/global/status"
mqtt_topic_inactive = "/global/inactive"
mqtt_topic_error = "/global/error"
mqtt_topic_control = "/units/{}/control".format(mqtt_unit_id)
mqtt_subscribe_topics = [mqtt_topic_status_request, mqtt_topic_control]


