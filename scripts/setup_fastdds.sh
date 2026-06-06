#!/usr/bin/env bash
set -eo pipefail

mkdir -p "$HOME/.ros"
cat > "$HOME/.ros/fastdds.xml" <<'XML'
<?xml version="1.0" encoding="UTF-8" ?>
<profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
  <transport_descriptors>
    <transport_descriptor>
      <transport_id>UdpTransport</transport_id>
      <type>UDPv4</type>
    </transport_descriptor>
  </transport_descriptors>

  <participant profile_name="udp_transport_profile" is_default_profile="true">
    <rtps>
      <userTransports>
        <transport_id>UdpTransport</transport_id>
      </userTransports>
      <useBuiltinTransports>false</useBuiltinTransports>
    </rtps>
  </participant>
</profiles>
XML

if ! grep -q "FASTRTPS_DEFAULT_PROFILES_FILE=.*fastdds.xml" "$HOME/.bashrc"; then
  echo "export FASTRTPS_DEFAULT_PROFILES_FILE=\$HOME/.ros/fastdds.xml" >> "$HOME/.bashrc"
fi

export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"
export FASTRTPS_DEFAULT_PROFILES_FILE="$HOME/.ros/fastdds.xml"

echo "FastDDS profile written to $HOME/.ros/fastdds.xml"
echo "RMW_IMPLEMENTATION=$RMW_IMPLEMENTATION"
echo "FASTRTPS_DEFAULT_PROFILES_FILE=$FASTRTPS_DEFAULT_PROFILES_FILE"
