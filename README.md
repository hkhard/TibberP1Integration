# Tibber P1 Meter Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This custom component integrates a P1 meter with Tibber API via Home Assistant.

## Installation

### HACS (Recommended)

1. Ensure you have [HACS](https://hacs.xyz/) installed in your Home Assistant instance.
2. In the HACS panel, go to "Integrations".
3. Click the "+" button and search for "Tibber P1 Meter".
4. Click "Install" on the Tibber P1 Meter integration.
5. Restart Home Assistant.

If you can't find the integration in HACS, you can add it as a custom repository:

1. In HACS, go to "Integrations".
2. Click on the three dots in the top right corner and select "Custom repositories".
3. Add the URL of this repository: `https://github.com/hkhard/TibberP1Integration`
4. Select "Integration" as the category.
5. Click "ADD".
6. The integration should now appear in the list of available integrations to install.

### Manual Installation

1. Download the `tibber_p1_meter` folder from this repository.
2. Copy the folder to your `custom_components` directory in your Home Assistant configuration directory.
   If you don't have a `custom_components` directory, you'll need to create one.
3. Restart Home Assistant.

## Configuration

1. In Home Assistant, go to Configuration > Integrations.
2. Click the "+" button to add a new integration.
3. Search for "Tibber P1 Meter" and select it.
4. Follow the configuration steps:
   - Enter your Tibber API Access Token.
   - Select the P1 meter entity from your existing entities.
   - Choose the appropriate sensors for energy consumption, current power, and optionally for energy production and current power production.

## Usage

After configuration, the integration will create several sensors:

- Tibber P1 Power: Shows the current power consumption.
- Tibber P1 Energy Consumption: Shows the accumulated energy consumption.
- Tibber P1 Energy Cost: Shows the accumulated energy cost (if available).

The integration will periodically update these sensors and send the data to your Tibber account.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
