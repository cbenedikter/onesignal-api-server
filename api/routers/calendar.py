# api/routers/calendar.py
"""
Calendar endpoints for generating Google Calendar URLs and ICS files
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from api.models.schemas import CalendarDataRequest, CalendarDataResponse
from api.services.calendar_service import calendar_service
from api.config import settings

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.post("-data", response_model=CalendarDataResponse)
async def create_calendar_event(request: CalendarDataRequest, http_request: Request):
    """
    Generate Google Calendar URL and ICS file from appointment data

    Receives appointment data from OneSignal data feeds and returns:
    - Google Calendar "add to calendar" URL
    - URL to download .ics calendar file

    Example payload:
    {
        "summary": "Booking Confirmation",
        "description": "Windglass Repair Appointment",
        "organizer_email": "claudio+1@onesignal.com",
        "attendees_emails": ["user@example.com"],
        "time_zone": "Europe/Helsinki",
        "location": "Workshop Name",
        "start_time": "16:00",
        "end_time": "17:00",
        "meeting_date": "25-12-2025",
        "glass_type": "windshield"
    }
    """
    try:
        # Build base URL from request
        base_url = str(http_request.base_url).rstrip('/')

        # Generate calendar data
        response = await calendar_service.generate_calendar_data(request, base_url)

        return response

    except Exception as e:
        print(f"❌ Error in calendar endpoint: {type(e).__name__}: {e}")
        return CalendarDataResponse(
            status="error",
            google_url=None,
            ics_url=None,
            message=f"Failed to generate calendar data: {str(e)}"
        )


@router.get("/{event_id}.ics")
async def download_ics_file(event_id: str):
    """
    Download ICS calendar file for a specific event

    Returns the .ics file content with proper Content-Type header
    for calendar applications to recognize and import.
    """
    # Retrieve ICS content from storage
    ics_content = await calendar_service.get_ics_content(event_id)

    if not ics_content:
        raise HTTPException(
            status_code=404,
            detail=f"Calendar event {event_id} not found or has expired"
        )

    # Return ICS file with proper headers
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="{event_id}.ics"'
        }
    )
