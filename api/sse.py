"""
Server-Sent Events (SSE) for real-time updates
"""
from flask import Blueprint, Response, stream_with_context
import json
import time

sse_bp = Blueprint('sse', __name__)

# Store for real-time events
events_queue = []

def add_event(event_type, data):
    """Add an event to the queue"""
    events_queue.append({
        'type': event_type,
        'data': data,
        'timestamp': time.time()
    })
    
    # Keep only last 100 events
    if len(events_queue) > 100:
        events_queue.pop(0)

@sse_bp.route('/events')
def stream_events():
    """Stream events to clients"""
    def generate():
        """Generate SSE events"""
        last_index = 0
        
        while True:
            # Send pending events
            if last_index < len(events_queue):
                for event in events_queue[last_index:]:
                    yield f"data: {json.dumps(event)}\n\n"
                last_index = len(events_queue)
            
            # Send heartbeat
            yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"
            time.sleep(1)
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

@sse_bp.route('/notify/<event_type>', methods=['POST'])
def notify_event(event_type):
    """Trigger a notification event"""
    from flask import request
    data = request.get_json() or {}
    add_event(event_type, data)
    return {'message': 'Event triggered'}, 200
