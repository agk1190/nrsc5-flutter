# Flutter Event Piping

This document describes the Flutter event piping feature added to nrsc5, which allows external applications (like Flutter apps) to receive real-time event data from the nrsc5 decoder.

## Overview

The `--flutter-pipe` option enables nrsc5 to output event data in JSON format to a file or named pipe (FIFO). This allows Flutter or other applications to display metadata, station information, and images without processing audio.

## Usage

### Basic Usage

```bash
# Create a named pipe (FIFO)
mkfifo /tmp/nrsc5_events

# Start nrsc5 with Flutter pipe output
nrsc5 --flutter-pipe /tmp/nrsc5_events 107.1 0
```

### Reading Events

In another terminal or process, read from the pipe:

```bash
# Simple reader
cat /tmp/nrsc5_events

# Or use the provided example
python3 flutter_reader_example.py /tmp/nrsc5_events
```

### Using a Regular File

Instead of a named pipe, you can also use a regular file:

```bash
nrsc5 --flutter-pipe /tmp/nrsc5_events.jsonl 107.1 0
```

## Event Format

Events are output as JSON objects, one per line (JSONL format). Each event has an `"event"` field indicating the event type.

### Event Types

#### Synchronization Events

**sync** - Decoder synchronized to signal
```json
{"event":"sync","freq_offset":95,"psmi":1}
```

**lost_sync** - Decoder lost synchronization
```json
{"event":"lost_sync"}
```

#### Station Information

**station_name** - Station call sign or name
```json
{"event":"station_name","name":"KUT "}
```

**station_slogan** - Station slogan/tagline
```json
{"event":"station_slogan","slogan":"The University of Texas at Austin"}
```

**station_message** - Station message
```json
{"event":"station_message","message":"Now playing..."}
```

**station_location** - Station coordinates
```json
{"event":"station_location","latitude":30.2850,"longitude":-97.7339,"altitude":200}
```

**station_id** - Station identification
```json
{"event":"station_id","country":"US","fcc_facility_id":12345}
```

#### ID3 Metadata

**id3** - ID3 tags (title, artist, album, genre)
```json
{"event":"id3","program":0,"title":"Song Title","artist":"Artist Name","album":"Album Name"}
```

Fields may include:
- `title` - Track title
- `artist` - Artist name
- `album` - Album name
- `genre` - Music genre
- `ufid_owner`, `ufid_id` - Unique file identifier
- `xhdr_param`, `xhdr_mime`, `xhdr_lot` - Extended header data
- `comments` - Array of comment objects with `lang`, `short_desc`, `text`

#### Signal Quality

**mer** - Modulation Error Ratio
```json
{"event":"mer","lower":13.4,"upper":12.4}
```

**ber** - Bit Error Rate
```json
{"event":"ber","cber":0.000186}
```

#### Images and Files

**lot** - LOT (Large Object Transfer) file received
```json
{
  "event":"lot",
  "lot":123,
  "name":"album_art.jpg",
  "size":45678,
  "mime":1234567890,
  "expiry":"2025-01-15T12:30:45Z",
  "data":"ffd8ffe000104a464946..."
}
```

The `data` field contains hex-encoded binary data. To decode:
```python
import binascii
binary_data = binascii.unhexlify(event['data'])
```

**here_image** - HERE traffic/weather map image
```json
{
  "event":"here_image",
  "type":"TRAFFIC",
  "seq":1,
  "n1":1,
  "n2":9,
  "time":"2025-01-15T12:30:45Z",
  "lat1":30.5000,
  "lon1":-98.0000,
  "lat2":30.0000,
  "lon2":-97.5000,
  "name":"trafficMap_1_1.png",
  "size":12345,
  "data":"89504e470d0a1a0a..."
}
```

#### Audio Service

**asd** - Audio Service Descriptor
```json
{"event":"asd","program":0,"access":"public","type":"Rock","sound_exp":0}
```

#### Emergency Alerts

**emergency_alert** - Emergency alert message
```json
{
  "event":"emergency_alert",
  "message":"Tornado warning in effect...",
  "category1":"Weather",
  "category2":"Safety"
}
```

When an alert ends:
```json
{"event":"emergency_alert","ended":true}
```

## Integration Examples

### Python Example

```python
import json

with open('/tmp/nrsc5_events', 'r') as pipe:
    for line in pipe:
        event = json.loads(line.strip())
        
        if event['event'] == 'id3':
            print(f"Now playing: {event.get('title', 'Unknown')}")
            print(f"Artist: {event.get('artist', 'Unknown')}")
        
        elif event['event'] == 'lot' and 'data' in event:
            # Save album art
            import binascii
            data = binascii.unhexlify(event['data'])
            with open(f"lot_{event['lot']}.jpg", 'wb') as f:
                f.write(data)
```

### Flutter/Dart Example

```dart
import 'dart:io';
import 'dart:convert';

void main() async {
  final pipe = File('/tmp/nrsc5_events');
  final lines = pipe.openRead()
    .transform(utf8.decoder)
    .transform(LineSplitter());
  
  await for (var line in lines) {
    final event = jsonDecode(line);
    
    switch (event['event']) {
      case 'id3':
        print('Now playing: ${event['title']}');
        break;
      case 'station_name':
        print('Station: ${event['name']}');
        break;
      case 'lot':
        if (event['data'] != null) {
          // Decode and display image
          final bytes = _hexToBytes(event['data']);
          // Display bytes as image...
        }
        break;
    }
  }
}

List<int> _hexToBytes(String hex) {
  return List.generate(hex.length ~/ 2, 
    (i) => int.parse(hex.substring(i * 2, i * 2 + 2), radix: 16));
}
```

### Node.js Example

```javascript
const fs = require('fs');
const readline = require('readline');

const rl = readline.createInterface({
  input: fs.createReadStream('/tmp/nrsc5_events'),
  crlfDelay: Infinity
});

rl.on('line', (line) => {
  const event = JSON.parse(line);
  
  if (event.event === 'id3') {
    console.log(`Now playing: ${event.title || 'Unknown'}`);
  } else if (event.event === 'lot' && event.data) {
    // Convert hex to buffer
    const buffer = Buffer.from(event.data, 'hex');
    fs.writeFileSync(`lot_${event.lot}.jpg`, buffer);
  }
});
```

## Notes

- Events are line-buffered for real-time delivery
- Audio and IQ data are NOT included in the event stream
- The pipe will block if no reader is connected (use `cat > /dev/null` as a dummy reader if needed)
- JSON strings are not escaped for special characters; ensure your JSON parser handles this
- For production use, consider error handling and reconnection logic
- Named pipes (FIFOs) provide better real-time performance than regular files

## Testing

To test the feature with the included sample file:

```bash
# Decompress sample
cd support
xz -d sample.xz

# Create pipe
mkfifo /tmp/test_pipe

# Start reader in background
python3 ../flutter_reader_example.py /tmp/test_pipe &

# Run nrsc5
cd ..
./build/src/nrsc5 --flutter-pipe /tmp/test_pipe -o /tmp/audio.wav -r support/sample 0
```

## Implementation Details

The Flutter piping feature is implemented with minimal changes to `main.c`:
- Added `flutter_pipe` field to `state_t` structure
- Added `write_flutter_event()` function to serialize events
- Modified `callback()` to call `write_flutter_event()` for each event
- Added `--flutter-pipe` command-line option
- Added cleanup code in `cleanup()` function

All changes are contained within `main.c` and are conditionally enabled only when the `--flutter-pipe` option is used, making the implementation non-intrusive and easy to maintain during rebases.
