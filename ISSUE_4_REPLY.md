## Configuration Solution Added

I've added a comprehensive AirSim configuration solution to address your settings.json needs:

### What's Been Added

- **`configs/settings.example.json`** - Production-ready AirSim configuration optimized for this project
- **`configs/README.md`** - Detailed setup guide and configuration explanations
- **Updated main README** with configuration section and quick setup instructions

### How to Use

1. **Copy the example configuration**:
   ```bash
   # Windows
   copy configs\settings.example.json %USERPROFILE%\Documents\AirSim\settings.json
   
   # macOS/Linux  
   cp configs/settings.example.json ~/Documents/AirSim/settings.json
   ```

2. **Restart AirSim completely** to apply the new settings

3. **Run the project** - it should now work seamlessly with the configured vehicle and camera setup

### Key Features

- **Car simulation mode** with PhysXCar vehicle
- **Single front camera** (`"0"`) - compatible with our robust image wrapper 
- **1280x720 resolution** at 90° FOV for optimal YOLO object detection
- **Performance optimized** for real-time simulation
- **Recording ready** (disabled by default to save storage)

### Customization

The configuration is designed to be extensible. You can easily:
- Add multiple cameras by extending the `Cameras` object
- Adjust resolution/FOV for different performance requirements  
- Enable recording by setting `RecordOnMove: true`
- Modify vehicle physics parameters as needed

For detailed customization options and troubleshooting, see [`configs/README.md`](configs/README.md).

This should resolve your AirSim setup issues. Let me know if you need any adjustments to the configuration!
