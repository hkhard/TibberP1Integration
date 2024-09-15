# Tibber P1 Meter Integration for Home Assistant

This project integrates the ESP8266 P1 meter with Tibber API via a Home Assistant custom component.

## Installation

### HACS (Recommended)

1. Ensure that [HACS](https://hacs.xyz/) is installed.
2. Search for "Tibber P1 Meter" in the HACS "Integrations" tab.
3. Click Install.
4. Restart Home Assistant.

### Manual Installation

1. Copy the `custom_components/tibber_p1_meter` directory to your Home Assistant's `custom_components` directory.
2. Restart Home Assistant.

## Configuration

1. In the Home Assistant UI, go to "Configuration" -> "Integrations" -> "Add Integration".
2. Search for "Tibber P1 Meter" and select it.
3. Follow the configuration steps to enter your Tibber API access token.

## ESP8266 Setup

Refer to the `esp8266_p1_meter/` directory for the Arduino sketch and setup instructions for the ESP8266 device.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
