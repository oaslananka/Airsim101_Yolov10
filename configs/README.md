# AirSim Configuration Guide

This directory contains example configuration files for AirSim simulation.

## Quick Setup

1. **Copy the example settings**:
   ```bash
   cp configs/settings.example.json ~/Documents/AirSim/settings.json
   ```

2. **For Windows users**:
   ```cmd
   copy configs\settings.example.json %USERPROFILE%\Documents\AirSim\settings.json
   ```

3. **Restart AirSim** to apply the new settings.

## Configuration Details

### `settings.example.json`
- **Vehicle**: PhysXCar (car simulation mode)
- **Camera**: Single front camera (`"0"`) 
- **Resolution**: 1280x720 pixels
- **Field of View**: 90 degrees
- **Position**: Centered front mount (-0.30m Z offset)
- **Recording**: Disabled by default (set `RecordOnMove: true` to enable)
- **Performance**: ClockSpeed 1 (real-time simulation)

### Key Settings Explained

- `"SimMode": "Car"` - Enables car physics and controls
- `"ClockSpeed": 1` - Real-time simulation (increase for faster, decrease for slower)
- `"Cameras": { "0": ... }` - Camera configuration (matches our robust wrapper)
- `"CaptureSettings"` - Image format, resolution, and quality settings
- `"Recording"` - Optional flight/drive recording configuration

## Camera Configuration

The example uses camera `"0"` which matches our robust image wrapper in `utils/robust_image.py`. This ensures compatibility with the object detection pipeline.

### Camera Position
- `X: 0.50` - 50cm forward from vehicle center
- `Y: 0.00` - Centered laterally  
- `Z: -0.30` - 30cm below vehicle center (front bumper level)

## Troubleshooting

- **Settings not applied**: Ensure AirSim is completely closed before copying settings
- **Camera not found**: Verify camera name matches (`"0"` not `"FrontCenter"`)
- **Performance issues**: Reduce `ClockSpeed` or image resolution
- **Recording issues**: Check disk space and set `RecordOnMove: true`

## Advanced Configuration

For advanced settings, see the [official AirSim documentation](https://github.com/Microsoft/AirSim/blob/main/docs/settings.md).

Common modifications:
- Multiple cameras: Add `"1"`, `"2"`, etc. to `Cameras` object
- Weather: Add `Weather` section for wind, rain, fog
- Physics: Modify `PhysicsEngineName` and related parameters
- API: Configure `ApiServerPort` and `IsApiEnabled`
