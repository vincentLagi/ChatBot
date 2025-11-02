import requests
from langchain.tools import tool


@tool("fetch_room_schedule_data")
def fetch_room_schedule_data(date: str) -> list:
    """Fetch empty rooms for a specific date from the SLC API.
    
    Args:
        date: The date in MM/DD/YYYY format
        
    Returns:
        List of room schedule
    """
    url = f"http://localhost:8080/get_all_room_schedule_by_date?startDate={date}&endDate={date}"
    response = requests.get(url)
    response.raise_for_status()
        
    return response.json()

@tool("fetch_job_data")
def fetch_job_data(username_and_date: str) -> str:
    """
    Fetch job data for a specific user and date.
    
    Input Format:
    - Provide input as "username,date" (comma-separated)
    
    Example:
    - "KA24-1,2025-07-09"
    
    Returns:
    - JSON string containing job data or error message
    """
    try:
        username, date = map(str.strip, username_and_date.split(","))
        url = "http://localhost:8080/job"
        params = {"username": username, "date": date}
        response = requests.get(url, params=params, verify=False)  # use verify=False only if self-signed cert

        if response.status_code == 200:
            job_data = response.json()
            if not job_data:
                return f"🗓️ No job found for {username} on {date}."
            return f"✅ Job data for {username} on {date}:\n\n{job_data}"
        else:
            return f"❌ Failed to fetch jobs: HTTP {response.status_code}"

    except ValueError:
        return "❌ Invalid input format. Use: 'username,date' (e.g., 'KA24-1,2025-07-09')"
    except Exception as e:
        return f"❌ Error fetching job data: {str(e)}"
    



@tool("fetch_empty_room_by_date")
def fetch_empty_room_by_date(date: str) -> list:
    """Fetch empty rooms for a specific date from the SLC API.
    
    Args:
        date: The date in MM/DD/YYYY format
        
    Returns:
        List of empty room numbers or error message
    """
    try:
        # Validate date format
        
        # Make API request
        url = f"http://localhost:8080/empty_room_schedule_by_date?startDate={date}&endDate={date}"
        
        response = requests.get(url)
        response.raise_for_status()
        
        return response.json()
    
    except ValueError:
        return {"error": "Invalid date format. Please use MM/DD/YYYY"}
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

@tool("fetch_empty_room_by_shift")
def fetch_empty_room_by_shift(date_and_shift: str) -> list:
    """Fetch empty rooms for a specific date and shift from the SLC API.
    
    Args:
        date: The date in MM/DD/YYYY format
        shift: The shift number (1-7)
        
    Returns:
        List of empty room numbers or error message
    """
    try:
        date, shift = map(str.strip, date_and_shift.split(","))
        
        url = f"http://localhost:8080/empty_room_schedule_by_shift?startDate={date}&endDate={date}&shift={shift}"
        
        response = requests.get(url)
        response.raise_for_status()
        
        return response.json()
    
    except ValueError:
        return {"error": "Invalid date format. Please use MM/DD/YYYY"}
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

@tool("check_empty_room_number_shift")
def check_empty_room_number_shift(room_number_date_shift: str) -> dict:
    """Check if a specific room is empty on a given date and shift.
    
    Args:
        room_number: The room number to check (e.g., "601")
        date: The date in MM/DD/YYYY format
        shift: The shift number (1-7)
        
    Returns:
        Dictionary with status ("Empty", "Not Empty", or "No Schedule") or error message
    """
    try:
        room_number, date, shift = map(str.strip, room_number_date_shift.split(","))
        url = f"http://localhost:8080/check_empty_room_by_number_and_shift?startDate={date}&endDate={date}&shift={shift}&roomNumber={room_number}"
        
        response = requests.get(url)
        response.raise_for_status()
        
        return response.json()
    
    except ValueError:
        return {"error": "Invalid date format. Please use MM/DD/YYYY"}
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


@tool("check_empty_room_number")
def check_empty_room_number(room_number_date: str)-> dict:
    """Check if a specific room is empty on a given date and shift.
    
    Args:
        room_number: The room number to check (e.g., "601")
        date: The date in MM/DD/YYYY format
        
    Returns:
        Dictionary with status ("Empty", "Not Empty", or "No Schedule") or error message
    """
    try:
        room_number, date = map(str.strip, room_number_date.split(","))
        url = f"http://localhost:8080/check_empty_room_by_number?startDate={date}&endDate={date}&roomNumber={room_number}"
        response = requests.get(url)
        response.raise_for_status()
        
        return response.json()
    
    except ValueError:
        return {"error": "Invalid date format. Please use MM/DD/YYYY"}
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}