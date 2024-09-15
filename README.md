# Tibber P1 Meter Integration for Home Assistant

This project integrates the ESP8266 P1 meter with Tibber API via a Home Assistant custom component.

## Installation

### HACS (Recommended)

1. Ensure that [HACS (Home Assistant Community Store)](https://hacs.xyz/) is installed in your Home Assistant instance.
   - If you haven't installed HACS yet, please follow the [official HACS installation guide](https://hacs.xyz/docs/installation/prerequisites).

2. In Home Assistant, navigate to HACS (sidebar) -> Integrations.

3. Click on the three dots in the top right corner and select "Custom repositories".

4. Add this repository URL: `https://github.com/hkhard/TibberP1Integration`
   - Category: Integration

5. Click the "+" button in the bottom right corner to add a new integration.

6. Search for "Tibber P1 Meter" and click on it.

7. Click on "Install" in the bottom right corner.

8. Restart Home Assistant to complete the installation.

### Manual Installation

If you prefer to install the integration manually:

1. Download the latest release from the [GitHub repository](https://github.com/hkhard/TibberP1Integration).
2. Extract the downloaded file.
3. Copy the `custom_components/tibber_p1_meter` directory to your Home Assistant's `custom_components` directory.
4. Restart Home Assistant.

## Configuration

1. In the Home Assistant UI, go to "Configuration" -> "Integrations" -> "Add Integration".
2. Search for "Tibber P1 Meter" and select it.
3. Follow the configuration steps to enter your Tibber API access token.
   - You can obtain your Tibber API access token from the [Tibber Developer Portal](https://developer.tibber.com/).

## ESP8266 Setup

Refer to the `esp8266_p1_meter/` directory in this repository for the Arduino sketch and detailed setup instructions for the ESP8266 device.

## Usage

After installation and configuration, the Tibber P1 Meter integration will create a sensor entity in Home Assistant. You can use this entity in your automations, scripts, or Lovelace UI to monitor and control your energy usage.

## Troubleshooting

If you encounter any issues:
1. Check the Home Assistant logs for any error messages related to the Tibber P1 Meter integration.
2. Ensure your Tibber API access token is correct and has the necessary permissions.
3. Verify that your ESP8266 device is correctly set up and communicating with your MQTT broker.

For more detailed troubleshooting steps, please refer to our [Troubleshooting Guide](https://github.com/hkhard/TibberP1Integration/wiki/Troubleshooting) in the wiki.

## Contributing

We welcome contributions to improve the Tibber P1 Meter Integration! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you need help or have any questions, please open an issue on our [GitHub Issues page](https://github.com/hkhard/TibberP1Integration/issues).

Thank you for using the Tibber P1 Meter Integration!
