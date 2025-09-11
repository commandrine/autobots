import requests
import os
from urllib.parse import urlparse, urljoin

def fetch_and_save_file(url, file_type, domain):
    """Fetches and saves a file, prepending the domain and returning success status."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        parsed_url = urlparse(url)
        path = parsed_url.path.lstrip("/") #remove leading slash to avoid issues
        path_parts = path.split("/")
        if path_parts and path_parts[-1] in ("robots.txt", "robot.txt"):
            path_parts.pop() #remove last part if its robots.txt or robot.txt
        sanitized_path = "_".join(path_parts)
        filename = f"{parsed_url.netloc}_{sanitized_path}_{file_type}.txt"
        filename = "".join(c for c in filename if c.isalnum() or c in "._-") # improved sanitization

        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(f"# Domain: {domain}\n")
            file.write(response.text)

        print(f"Downloaded {file_type} from {url} to {filepath}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {file_type} from {url}: {e}")
        return False
    except OSError as e:
        print(f"Error saving file: {e}")
        return False

def check_robots_txt(url):
    """Checks for robots.txt and robot.txt, returning success counts."""
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = "http://" + url
            parsed_url = urlparse(url)
        domain = parsed_url.netloc

        robots_success = 0
        robot_success = 0

        if domain:
            robots_url = urljoin(url, "robots.txt")
            if fetch_and_save_file(robots_url, "robots.txt", domain):
                robots_success = 1

            robot_url = urljoin(url, "robot.txt")
            if fetch_and_save_file(robot_url, "robot.txt", domain):
                robot_success = 1
        else:
            print(f"Invalid URL Format: {url}")
        return robots_success, robot_success
    except Exception as e:
        print(f"An unexpected error occurred in check_robots_txt: {e}")
        return 0, 0

def process_urls(urls):
    """Processes a list of URLs and summarizes results."""
    total_robots = 0
    successful_robots = 0
    total_robot = 0
    successful_robot = 0

    for url in urls:
        print(f"Checking URL: {url}")
        robots_s, robot_s = check_robots_txt(url)
        total_robots += 1
        successful_robots += robots_s
        total_robot += 1
        successful_robot += robot_s
        print("-" * 20)

    print("\n--- Summary ---")
    print(f"Checked {total_robots} robots.txt files. Successfully downloaded: {successful_robots} ({ (successful_robots/total_robots)*100:.2f}%)" if total_robots >0 else f"No robots.txt files checked.")
    print(f"Checked {total_robot} robot.txt files. Successfully downloaded: {successful_robot} ({ (successful_robot/total_robot)*100:.2f}%)" if total_robot >0 else f"No robot.txt files checked.")

if __name__ == "__main__":
    while True:
        try:
            choice = input("Enter '1' to input URL manually or '2' to read from a file (or 'q' to quit): ")
            if choice == '1':
                url = input("Enter the URL: ")
                process_urls([url])
            elif choice == '2':
                file_path = input("Enter the path to the text file: ")
                try:
                    with open(file_path, 'r', encoding="utf-8") as file:
                        urls = [line.strip() for line in file.readlines() if line.strip()]
                    process_urls(urls)
                except FileNotFoundError:
                    print(f"File not found: {file_path}")
            elif choice.lower() == 'q':
                break
            else:
                print("Invalid choice. Please enter '1', '2', or 'q'.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        print("\n")