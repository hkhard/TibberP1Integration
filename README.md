# Tibber P1 Meter Integration for Home Assistant

This project integrates the ESP8266 P1 meter with Tibber API via a Home Assistant custom component.

## Setup Instructions

1. Create a new GitHub repository:
   - Go to https://github.com/new
   - Repository name: TibberP1Integration
   - Description: ESP8266 P1 meter integration to update Tibber API via Home Assistant custom component
   - Choose "Public" or "Private" based on your preference
   - Initialize this repository with a README (uncheck this option)
   - Click "Create repository"

2. After creating the repository, you'll see a page with instructions. Look for the section "…or push an existing repository from the command line" and copy the commands provided.

3. Run the following commands in your local project directory:
   ```
   git remote set-url origin https://github.com/hkhard/TibberP1Integration.git
   git branch -M main
   git push -u origin main
   ```

4. Refresh your GitHub repository page to see the uploaded files.

## Project Structure

- `esp8266_p1_meter/`: Contains the Arduino sketch for the ESP8266
- `custom_components/tibber_p1_meter/`: Home Assistant custom component
- `configuration.yaml`: Example Home Assistant configuration

## Installation

Refer to the documentation in the `custom_components/tibber_p1_meter/` directory for installation instructions.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
