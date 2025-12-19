# api/services/calendar_service.py
"""
Service for generating calendar events and links
"""
import uuid
from datetime import datetime
from urllib.parse import urlencode
from typing import Dict, Optional
import pytz
from icalendar import Calendar, Event, vCalAddress, vText
from api.storage.kv_store import KVStore
from api.models.schemas import CalendarDataRequest, CalendarDataResponse
from api.config import settings


class CalendarService:
    def __init__(self):
        self.kv_store = KVStore()
        self.settings = settings
        self.ics_ttl = 30 * 24 * 60 * 60  # 30 days in seconds

    async def generate_calendar_data(self, request: CalendarDataRequest, base_url: str) -> CalendarDataResponse:
        """
        Generate Google Calendar URL and ICS file from appointment data

        Args:
            request: Calendar data from OneSignal
            base_url: Base URL for the API (for generating ics_url)

        Returns:
            CalendarDataResponse with google_url and ics_url
        """
        try:
            print(f"📅 Generating calendar data for: {request.summary}")

            # 1. Parse date and time
            start_dt, end_dt = self._parse_datetime(
                request.meeting_date,
                request.start_time,
                request.end_time,
                request.time_zone
            )

            # 2. Generate unique ID for this event
            event_id = str(uuid.uuid4())

            # 3. Generate Google Calendar URL
            google_url = self._generate_google_calendar_url(
                request, start_dt, end_dt
            )

            # 4. Generate ICS file content
            ics_content = self._generate_ics_content(
                request, start_dt, end_dt, event_id
            )

            # 5. Store ICS content in KV store
            self.kv_store.set(
                key=f"calendar_ics:{event_id}",
                value={
                    "ics_content": ics_content,
                    "created_at": datetime.utcnow().isoformat()
                },
                ttl=self.ics_ttl
            )

            # 6. Build ICS URL
            ics_url = f"{base_url}/calendar/{event_id}.ics"

            print(f"✅ Calendar data generated successfully: {event_id}")

            return CalendarDataResponse(
                status="success",
                google_url=google_url,
                ics_url=ics_url
            )

        except Exception as e:
            print(f"❌ Error generating calendar data: {type(e).__name__}: {e}")
            # Return partial success if possible
            return CalendarDataResponse(
                status="error",
                google_url=None,
                ics_url=None,
                message=f"Error generating calendar data: {str(e)}"
            )

    def _parse_datetime(
        self,
        meeting_date: str,
        start_time: str,
        end_time: str,
        timezone_str: str
    ) -> tuple[datetime, datetime]:
        """
        Parse date and time strings into timezone-aware datetime objects

        Args:
            meeting_date: Date in DD-MM-YYYY format
            start_time: Time in HH:MM format
            end_time: Time in HH:MM format
            timezone_str: IANA timezone string (e.g., "Europe/Helsinki")

        Returns:
            Tuple of (start_datetime, end_datetime) as timezone-aware objects
        """
        # Parse date (DD-MM-YYYY)
        day, month, year = meeting_date.split('-')

        # Parse start time (HH:MM)
        start_hour, start_minute = start_time.split(':')

        # Parse end time (HH:MM)
        end_hour, end_minute = end_time.split(':')

        # Get timezone
        tz = pytz.timezone(timezone_str)

        # Create datetime objects
        start_dt = tz.localize(datetime(
            int(year), int(month), int(day),
            int(start_hour), int(start_minute), 0
        ))

        end_dt = tz.localize(datetime(
            int(year), int(month), int(day),
            int(end_hour), int(end_minute), 0
        ))

        return start_dt, end_dt

    def _generate_google_calendar_url(
        self,
        request: CalendarDataRequest,
        start_dt: datetime,
        end_dt: datetime
    ) -> str:
        """
        Generate Google Calendar "add to calendar" URL

        Args:
            request: Calendar data request
            start_dt: Start datetime
            end_dt: End datetime

        Returns:
            Google Calendar URL
        """
        # Format dates for Google Calendar (YYYYMMDDTHHmmssZ in UTC)
        start_utc = start_dt.astimezone(pytz.UTC)
        end_utc = end_dt.astimezone(pytz.UTC)

        # Format: 20251225T140000Z
        dates_str = f"{start_utc.strftime('%Y%m%dT%H%M%SZ')}/{end_utc.strftime('%Y%m%dT%H%M%SZ')}"

        # Build description with additional details
        description_parts = [request.description]
        if request.glass_type:
            description_parts.append(f"Glass Type: {request.glass_type}")
        description_parts.append(f"Organizer: {request.organizer_email}")
        full_description = "\n".join(description_parts)

        # Build query parameters
        params = {
            'action': 'TEMPLATE',
            'text': request.summary,
            'dates': dates_str,
            'details': full_description,
            'location': request.location,
            'ctz': request.time_zone
        }

        # Add attendees if present (comma-separated)
        if request.attendees_emails:
            params['add'] = ','.join(request.attendees_emails)

        # Generate URL
        base_url = "https://calendar.google.com/calendar/render"
        query_string = urlencode(params)

        return f"{base_url}?{query_string}"

    def _generate_ics_content(
        self,
        request: CalendarDataRequest,
        start_dt: datetime,
        end_dt: datetime,
        event_id: str
    ) -> str:
        """
        Generate ICS (iCalendar) file content

        Args:
            request: Calendar data request
            start_dt: Start datetime
            end_dt: End datetime
            event_id: Unique event identifier

        Returns:
            ICS file content as string
        """
        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//OneSignal Calendar Integration//EN')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')

        # Create event
        event = Event()
        event.add('uid', f'{event_id}@onesignal-calendar')
        event.add('dtstamp', datetime.utcnow())
        event.add('dtstart', start_dt)
        event.add('dtend', end_dt)
        event.add('summary', request.summary)

        # Add description with custom fields
        description_parts = [request.description]
        if request.glass_type:
            description_parts.append(f"Glass Type: {request.glass_type}")
        event.add('description', '\n'.join(description_parts))

        # Add location
        event.add('location', request.location)

        # Add organizer
        organizer = vCalAddress(f'MAILTO:{request.organizer_email}')
        organizer.params['cn'] = vText(request.organizer_email)
        event.add('organizer', organizer)

        # Add attendees
        for attendee_email in request.attendees_emails:
            attendee = vCalAddress(f'MAILTO:{attendee_email}')
            attendee.params['cn'] = vText(attendee_email)
            attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
            attendee.params['PARTSTAT'] = vText('NEEDS-ACTION')
            attendee.params['RSVP'] = vText('TRUE')
            event.add('attendee', attendee)

        # Add event to calendar
        cal.add_component(event)

        # Return as string
        return cal.to_ical().decode('utf-8')

    async def get_ics_content(self, event_id: str) -> Optional[str]:
        """
        Retrieve ICS content from storage

        Args:
            event_id: Unique event identifier

        Returns:
            ICS file content or None if not found
        """
        try:
            data = self.kv_store.get(f"calendar_ics:{event_id}")
            if data:
                print(f"📅 Retrieved ICS content for event: {event_id}")
                return data.get("ics_content")
            else:
                print(f"❌ ICS content not found for event: {event_id}")
                return None
        except Exception as e:
            print(f"❌ Error retrieving ICS content: {type(e).__name__}: {e}")
            return None


# Singleton instance
calendar_service = CalendarService()
