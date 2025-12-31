#!/usr/bin/env python3
"""
Example event reader for nrsc5 JSON output.
This demonstrates how an application would read and parse the JSON events.

Usage:
    1. Create a named pipe: mkfifo /tmp/nrsc5_pipe
    2. Run this script: python3 json_reader_example.py /tmp/nrsc5_pipe
    3. In another terminal: nrsc5 --json-output /tmp/nrsc5_pipe [other options] frequency program
    
    Or with stdout mode:
    nrsc5 --json-stdout [other options] frequency program | python3 json_reader_example.py /dev/stdin
"""

import sys
import json

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 json_reader_example.py <pipe_path>")
        sys.exit(1)
    
    pipe_path = sys.argv[1]
    
    print(f"Opening pipe at {pipe_path}...")
    print("Waiting for nrsc5 events...\n")
    
    with open(pipe_path, 'r') as pipe:
        for line in pipe:
            line = line.strip()
            if not line:
                continue
            
            try:
                event = json.loads(line)
                handle_event(event)
            except json.JSONDecodeError as e:
                print(f"ERROR parsing JSON: {e}")
                print(f"Line: {line}")

def handle_event(event):
    """Process an event from nrsc5."""
    event_type = event.get('event')
    
    if event_type == 'sync':
        print(f"📡 SYNC: Frequency offset: {event['freq_offset']} Hz, PSMI: {event['psmi']}")
    
    elif event_type == 'lost_sync':
        print("⚠️  LOST SYNC")
    
    elif event_type == 'station_name':
        print(f"📻 Station: {event['name']}")
    
    elif event_type == 'station_slogan':
        print(f"💬 Slogan: {event['slogan']}")
    
    elif event_type == 'station_message':
        print(f"💬 Message: {event['message']}")
    
    elif event_type == 'station_location':
        print(f"📍 Location: {event['latitude']}, {event['longitude']} @ {event['altitude']}m")
    
    elif event_type == 'station_id':
        print(f"🆔 Station ID: {event['country']} FCC: {event['fcc_facility_id']}")
    
    elif event_type == 'id3':
        parts = []
        if 'title' in event:
            parts.append(f"Title: {event['title']}")
        if 'artist' in event:
            parts.append(f"Artist: {event['artist']}")
        if 'album' in event:
            parts.append(f"Album: {event['album']}")
        if parts:
            print(f"🎵 ID3: {' | '.join(parts)}")
    
    elif event_type == 'mer':
        print(f"📊 MER: Lower={event['lower']} dB, Upper={event['upper']} dB")
    
    elif event_type == 'ber':
        print(f"📊 BER: {event['cber']:.6f}")
    
    elif event_type == 'lot':
        size_kb = event['size'] / 1024
        print(f"📦 LOT File: {event['name']} ({size_kb:.1f} KB) - Expires: {event['expiry']}")
        if 'data' in event:
            print(f"   Data length: {len(event['data']) // 2} bytes (hex encoded)")
    
    elif event_type == 'here_image':
        size_kb = event['size'] / 1024
        print(f"🗺️  HERE Image: {event['type']} - {event['name']} ({size_kb:.1f} KB)")
        print(f"   Bounds: ({event['lat1']}, {event['lon1']}) to ({event['lat2']}, {event['lon2']})")
        if 'data' in event:
            print(f"   Data length: {len(event['data']) // 2} bytes (hex encoded)")
    
    elif event_type == 'asd':
        print(f"🔊 Audio Service: Program {event['program']} - {event['access']} - {event['type']}")
    
    elif event_type == 'emergency_alert':
        if event.get('ended'):
            print("🚨 Emergency Alert ENDED")
        else:
            msg = event.get('message', 'No message')
            print(f"🚨 EMERGENCY ALERT: {msg}")
            if 'category1' in event:
                print(f"   Category: {event['category1']}")
    
    else:
        print(f"❓ Unknown event: {event_type}")

if __name__ == '__main__':
    main()
