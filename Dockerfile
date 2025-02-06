name: "Edge Impulse Person Detector"
version: "1.0.0"
slug: "edge_impulse_person_detector"
description: "Person detection using Edge Impulse"
url: "https://github.com/MusicMano/ha-person-detector"
arch:
  - aarch64
  - amd64
  - armhf
  - armv7
  - i386
init: false
startup: application
boot: auto
s6_overlay_version: 3
privileged:
  - NET_ADMIN
  - SYS_ADMIN
devices:
  - /dev/mem
homeassistant_api: true
host_network: true
options:
  camera_entity: "camera.esp32_cam"
  confidence_threshold: 0.7
  scan_interval: 1
schema:
  camera_entity: "str"
  confidence_threshold: "float"
  scan_interval: "int"
stage: "experimental"