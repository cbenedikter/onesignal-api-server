# api/routers/dashboard.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from ..storage.kv_store import kv_store

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

@router.get("", response_class=HTMLResponse)
async def view_dashboard():
    """View OneSignal response logs dashboard"""
    
    # Get all delivery logs from KV
    all_logs = []
    log_keys = await kv_store.get_keys("delivery_log:*")
    
    for key in log_keys:
        log_data = await kv_store.get(key)
        if log_data:
            all_logs.append(log_data)
    
    # Sort by timestamp (newest first)
    all_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Build HTML
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OneSignal Response Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .log-entry { 
                border: 1px solid #ddd; 
                padding: 15px; 
                margin: 10px 0;
                border-radius: 5px;
                background: #f9f9f9;
            }
            .success { border-left: 5px solid #4CAF50; }
            .error { border-left: 5px solid #f44336; }
            .timestamp { color: #666; font-size: 0.9em; }
            h1 { color: #333; }
            .response { 
                background: #fff; 
                padding: 10px; 
                border-radius: 3px;
                margin-top: 10px;
                font-family: monospace;
                font-size: 0.85em;
                white-space: pre-wrap;
            }
            .status { font-weight: bold; color: #2196F3; }
        </style>
        <meta http-equiv="refresh" content="10">
    </head>
    <body>
        <h1>🚚 OneSignal Delivery Notifications Dashboard</h1>
        <p>Auto-refreshes every 10 seconds | Found """ + str(len(all_logs)) + """ logs</p>
        <hr>
    """
    
    if not all_logs:
        html += "<p>No delivery logs found yet. Send a delivery request to see logs!</p>"
    
    for log in all_logs:
        response = log.get('response', {})
        is_success = 'id' in response
        
        html += f"""
        <div class="log-entry {'success' if is_success else 'error'}">
            <div><span class="status">{log.get('status', 'Unknown')}</span> - 
                 Tracking ID: {log.get('tracking_id', 'Unknown')}</div>
            <div class="timestamp">{log.get('timestamp', 'No timestamp')}</div>
            <div class="response">{str(response)}</div>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    return html