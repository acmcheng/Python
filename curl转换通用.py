import requests
import json
import pyperclip
from typing import Optional, Dict, Any
import sys

class CurlConverter:
    def __init__(self):
        self.url = "https://serverapi.trumanwl.com/api/curl-convert"
        self.headers = {
            "sec-ch-ua-platform": '"Windows"',
            "Referer": "https://trumanwl.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            "Content-Type": "application/json",
            "sec-ch-ua-mobile": "?0",
            "Origin": "https://trumanwl.com"
        }

    def get_clipboard_content(self) -> str:
        """Get content from clipboard with error handling."""
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Error reading from clipboard: {e}")
            sys.exit(1)

    def send_request(self, curl_content: str) -> Optional[Dict[str, Any]]:
        """Send POST request to convert curl command."""
        try:
            data = {
                "language": "python",
                "content": curl_content
            }
            response = requests.post(self.url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error making request: {e}")
            return None
        except json.JSONDecodeError:
            print("Error: Invalid JSON response from server")
            return None

    def process_content(self, content: str) -> str:
        """Process the content by removing comments and formatting."""
        lines = content.splitlines()
        non_comment_lines = [line for line in lines if not line.strip().startswith('#')]
        content_without_comments = '\n'.join(non_comment_lines)
        
        return f"""import json
{content_without_comments}
try:
    parsed_data = json.loads(response.text)
    formatted_json = json.dumps(parsed_data, indent=4, ensure_ascii=False)
    print(formatted_json)
except json.JSONDecodeError as e:
    print(f"Error parsing response: {{e}}")
    print("Raw response:", response.text)
"""

    def copy_to_clipboard(self, content: str) -> None:
        """Copy content to clipboard with error handling."""
        try:
            pyperclip.copy(content)
            print("Successfully copied to clipboard!")
        except Exception as e:
            print(f"Error copying to clipboard: {e}")

    def run(self) -> None:
        """Main execution flow."""
        # Get curl command from clipboard
        curl_content = self.get_clipboard_content()
        if not curl_content:
            print("No content found in clipboard")
            return

        # Send request and get response
        response_data = self.send_request(curl_content)
        if not response_data:
            return

        # Process content
        try:
            content = response_data["content"]
            output = self.process_content(content)
            
            # Print and copy result
            print("\nGenerated code:")
            print("-" * 50)
            print(output)
            print("-" * 50)
            self.copy_to_clipboard(output)
            
        except KeyError:
            print("Error: Response missing 'content' field")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    converter = CurlConverter()
    converter.run()
