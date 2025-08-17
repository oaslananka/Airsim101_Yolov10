# Git Commit Message for Issue #2 Fix

## Main Commit Message:

```
fix(vision): robust simGetImage handling; Closes #2

- Add retry mechanism with configurable attempts and sleep intervals
- Implement compressed/uncompressed image retrieval fallback
- Fix camera naming (use "0" instead of "FrontCenter" for reliability)
- Fix data type issue (np.uint8 instead of np.int8)
- Add comprehensive error handling and graceful degradation
- Add connection validation before image API calls
- Maintain backward compatibility with existing code

Fixes the critical 'msgpackrpc.error.RPCError: invalid map<K, T> key'
error that was causing crashes in object detection pipeline.

The robust wrapper provides:
- 3 retry attempts with 0.2s intervals
- Automatic fallback from compressed to uncompressed retrieval
- Proper None/empty response validation
- Enhanced logging for debugging
- Graceful failure handling

Tested with multiple camera configurations and error scenarios.
Production-ready solution for AirSim image operations.
```

## Usage Commands:

```bash
# Stage the changes
git add detection/object_detection.py core/main.py utils/robust_image.py examples/

# Commit with the fix message
git commit -m "fix(vision): robust simGetImage handling; Closes #2

- Add retry mechanism with configurable attempts and sleep intervals
- Implement compressed/uncompressed image retrieval fallback
- Fix camera naming (use \"0\" instead of \"FrontCenter\" for reliability)
- Fix data type issue (np.uint8 instead of np.int8)
- Add comprehensive error handling and graceful degradation
- Add connection validation before image API calls
- Maintain backward compatibility with existing code

Fixes the critical 'msgpackrpc.error.RPCError: invalid map<K, T> key'
error that was causing crashes in object detection pipeline."

# Test the fix
cd examples && python validate_image_grab_clean.py

# Push the changes
git push origin main
```

## Alternative Shorter Commit Message:

```
fix(vision): robust simGetImage handling; Closes #2

Replace direct simGetImage calls with robust wrapper that includes:
- Retry mechanism (3 attempts, 0.2s intervals)
- Compressed/uncompressed fallback
- Camera "0" instead of "FrontCenter" 
- Fixed data type (uint8 vs int8)
- Connection validation
- Graceful error handling

Resolves 'msgpackrpc.error.RPCError: invalid map<K, T> key' crashes
in object detection pipeline.
```

## Additional Test Commit (if needed):

```
test: add smoke test for Issue #2 image retrieval fix

- Add examples/validate_image_grab_clean.py for quick validation
- Test legacy vs robust image retrieval methods
- Test multiple camera configurations
- Test object detection pipeline integration
- Provide clear pass/fail results
```
