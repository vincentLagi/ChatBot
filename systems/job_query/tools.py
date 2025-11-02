import requests
from langchain.tools import tool

@tool("fetch_job_data")
def fetch_job_data(username: str) -> str:
    """
    Fetch job data for a specific user using only the username.
    
    Input Format:
    - Provide input as the username string (e.g., "KA24-1")
    
    Returns:
    - JSON string containing job data or error message
    """
    try:
        username = username.strip().upper()
        url = "http://localhost:8080/data_job"
        params = {"username": username}
        response = requests.get(url, params=params, verify=False)  # Don't use verify=False in production

        if response.status_code == 200:
            job_data = response.json()
            if not job_data:
                return f"🗓 No job found for {username}."
            return f"✅ Job data for {username}:\n\n{job_data}"
        else:
            return f"❌ Failed to fetch jobs: HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Error fetching job data: {str(e)}"
    

@tool("fetch_teaching_data")
def fetch_teaching_data(username: str) -> str:
    """
    Fetch overall job data summary for a specific user using only the username.

    Input Format:
    - Provide input as the username string (e.g., "KA24-1")

    Returns:
    - JSON string containing overall job summary or an error message
    """
    try:
        username = username.strip().upper()
        url = "http://localhost:8080/overall_job"
        params = {"username": username}
        response = requests.get(url, params=params, verify=False)  # Don't use verify=False in production

        if response.status_code == 200:
            overall_data = response.json()
            if not overall_data:
                return f"📊 No overall job data found for {username}."
            return f"✅ Overall job summary for {username}:\n\n{overall_data}"
        else:
            return f"❌ Failed to fetch overall job data: HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Error fetching overall job data: {str(e)}"