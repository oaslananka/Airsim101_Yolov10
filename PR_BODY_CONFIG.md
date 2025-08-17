# Add example AirSim configuration for optimal simulation setup

## Why Example Configuration is Needed

Many users struggle with AirSim setup and experience suboptimal performance due to misconfigured settings. Common issues include:

- **Incompatible camera configurations** causing image retrieval failures
- **Performance problems** from untuned simulation parameters
- **Missing vehicle setup** leading to connection errors
- **Unclear documentation** on optimal settings for object detection workflows

This PR provides a production-ready configuration template that ensures reliable operation with our robust image wrapper and YOLO detection pipeline.

## Configuration Details

### `configs/settings.example.json`
- **Vehicle**: PhysXCar with optimized physics settings
- **Camera**: Single front camera (`"0"`) matching our robust wrapper expectations
- **Resolution**: 1280x720 for optimal object detection performance
- **FOV**: 90° field of view for comprehensive scene coverage
- **Recording**: Pre-configured but disabled by default to avoid storage issues

### `configs/README.md`
- **Step-by-step setup guide** with platform-specific commands
- **Detailed parameter explanations** for customization
- **Troubleshooting section** for common configuration issues
- **Advanced configuration** references for power users

## Usage Instructions

### Quick Setup (Copy to AirSim directory)

**Windows:**
```cmd
copy configs\settings.example.json %USERPROFILE%\Documents\AirSim\settings.json
```

**Unix/Linux/macOS:**
```bash
cp configs/settings.example.json ~/Documents/AirSim/settings.json
```

### Important Notes
- **Restart AirSim** completely after copying settings
- **Backup existing settings** if you have custom configurations
- **Camera naming**: Uses `"0"` (not `"FrontCenter"`) for compatibility with Issue #2 fix
- **Performance**: Tuned for real-time simulation on standard hardware

## Documentation Integration

The main README.md now includes a dedicated **"Configurations"** section with:
- Quick setup commands
- Links to detailed documentation
- Integration with existing project workflow

For comprehensive setup guide, see [`configs/README.md`](configs/README.md).

## Benefits

- **Plug-and-play setup**: No manual configuration tweaking required
- **Guaranteed compatibility**: Tested with robust image wrapper and object detection
- **Performance optimized**: Balanced quality and simulation speed
- **Future-proof**: Extensible template for advanced scenarios

Relates to #4
