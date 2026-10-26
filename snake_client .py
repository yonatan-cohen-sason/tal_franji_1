import curses
import time
import requests


SERVER_URL = "http://localhost:8080"


def client_loop(stdscr):
    # Setup curses
    curses.curs_set(0)
    stdscr.nodelay(1)
    
    current_k = 0
    
    while True:
        try:
            # Get key input
            key = stdscr.getch()
            
            # Prepare request parameters
            params = {'k': current_k}
            if key != -1:
                params['key'] = key
            
            # Send request
            response = requests.get(SERVER_URL, params=params)
            
            if response.status_code == 200:
                updates = response.json()
                
                # Apply updates
                # updates is a list of [y, x, char]
                for y, x, char in updates:
                    try:
                        stdscr.addstr(y, x, char)
                    except curses.error:
                        # Ignore errors if drawing outside screen bounds
                        pass
                
                if updates:
                    stdscr.refresh()
                    current_k += len(updates)
            
            # Check for local quit (optional, but good to have)
            if key == 27 or key == ord('q') or key == ord('Q'):
                break
                
            time.sleep(0.1)
            
        except requests.RequestException as e:
            stdscr.addstr(0, 0, f"Connection error: {e}")
            stdscr.refresh()
            time.sleep(1)
        except Exception as e:
            stdscr.addstr(0, 0, f"Error: {e}")
            stdscr.refresh()
            time.sleep(1)

def main():
    try:
        curses.wrapper(client_loop)
    except KeyboardInterrupt:
        pass
    print("Exited client.")

if __name__ == "__main__":
    main()
