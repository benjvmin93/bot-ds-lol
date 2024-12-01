import requests
import enum

class RESPONSE_ERRORS(enum.Enum):
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    DATA_NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    UNSUPPORTED_MEDIA_TYPE = 415
    RATE_LIMIT_EXCEEDED = 429
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504

class LolApiWrapper:
    def __init__(self, api_key: str, region: str):
        """
        Initialize the API wrapper.
        """
        self._key = api_key
        self.region = region
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Riot-Token": self._key
        }
    
    def handle_error(self, response: requests.Response):
        """
        Handle HTTP response errors based on status codes.
        """
        try:
            status = response.json().get("status", {})
            status_code = status.get("status_code", response.status_code)
            message = status.get("message", "Unknown error")
        except ValueError:
            status_code = response.status_code
            message = response.text or "Unknown error"

        error_map = {
            RESPONSE_ERRORS.BAD_REQUEST.value: "Bad Request: Check your parameters.",
            RESPONSE_ERRORS.UNAUTHORIZED.value: "Unauthorized: Verify your API key.",
            RESPONSE_ERRORS.FORBIDDEN.value: "Forbidden: You don't have access to this resource.",
            RESPONSE_ERRORS.DATA_NOT_FOUND.value: "Data Not Found: The requested resource doesn't exist.",
            RESPONSE_ERRORS.METHOD_NOT_ALLOWED.value: "Method Not Allowed: Invalid HTTP method used.",
            RESPONSE_ERRORS.UNSUPPORTED_MEDIA_TYPE.value: "Unsupported Media Type: Check your headers or payload.",
            RESPONSE_ERRORS.RATE_LIMIT_EXCEEDED.value: "Rate Limit Exceeded: Slow down your requests.",
            RESPONSE_ERRORS.INTERNAL_SERVER_ERROR.value: "Internal Server Error: The server encountered an error.",
            RESPONSE_ERRORS.BAD_GATEWAY.value: "Bad Gateway: The server is down or unreachable.",
            RESPONSE_ERRORS.SERVICE_UNAVAILABLE.value: "Service Unavailable: Try again later.",
            RESPONSE_ERRORS.GATEWAY_TIMEOUT.value: "Gateway Timeout: The server didn't respond in time."
        }
        
        error_message = error_map.get(status_code, f"Unexpected error occurred: {status_code}")
        raise Exception(f"{error_message}\nDetails: {message}")

    @property
    def _url_prefix(self):
        """
        Construct the base URL for API requests.
        """
        return f"https://{self.region}.api.riotgames.com"

    def _make_request(self, endpoint: str):
        """
        Perform a GET request and handle errors.
        """
        url = f"{self._url_prefix}{endpoint}"
        response = requests.get(url, headers=self._headers)
        if response.status_code != 200:
            self.handle_error(response)
        return response.json()
    
    def get_account_by_id(self, gameName: str, tagLine: str):
        """
        GET /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}
        """
        endpoint = f"/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
        return self._make_request(endpoint)
    
    def get_current_game_infos_by_puuid(self, puuid: str):
        """
        GET /lol/spectator/v5/active-games/by-summoner/{encryptedPUUID}
        """
        endpoint = f"/lol/spectator/v5/active-games/by-summoner/{puuid}"
        return self._make_request(endpoint)

def main():
    api_key = "RGAPI-0ad14448-dd66-4b82-a779-adf09c728458"
    region = "europe"
    
    lolapi = LolApiWrapper(api_key=api_key, region=region)
    
    # Fetch account details
    account = lolapi.get_account_by_id("CoffeeMaka", "ouaff")
    print("Account Details:", account)
    
    puuid = account.get("puuid")
    if puuid:
        print(f"PUUID of CoffeeMaka: {puuid}")
        lolapi.region = "euw1"
        # Fetch game information
        game_infos = lolapi.get_current_game_infos_by_puuid(puuid)
        print("Current Game Infos:", game_infos)
    else:
        print("No PUUID found for the given account.")

if __name__ == "__main__":
    main()
