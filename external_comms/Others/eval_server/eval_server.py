# Changing the actions in self.actions should automatically change the script to function with the new number of moves.
# Developed and improved by past CG4002 TAs and students: Tean Zheng Yang, Jireh Tan, Boyd Anderson,
# Paul Tan, Bernard Tan Ke Xuan, Ashley Ong, Kennard Ng, Xen Santos

import os
import sys
import time
import traceback
import random

import socket
import threading

import base64
import tkinter as tk
from tkinter import ttk
from tkinter.constants import HORIZONTAL, VERTICAL
import pandas as pd
from Crypto.Cipher import AES


LOG_DIR = os.path.join(os.path.dirname(__file__), 'evaluation_logs')
MESSAGE_SIZE = 2 
ACTIONS = ["shoot", "shield", "grenade", "reload"]
NUM_ACTION_REPEATS = 4

"""
Class that will generate randomized list of actions.
Actions will be displayed on the evaluation server UI for the 
players to follow. 
"""
class TurnGenerator():
    def __init__(self):
        self.cur_turn = 0
        
        self.num_actions = len(ACTIONS)
        
        # Generate random sequence of actions for Player 1
        self.p1_actions = ACTIONS * NUM_ACTION_REPEATS
        random.shuffle(self.p1_actions)
        self.p1_actions.insert(0, "none")
        self.p1_actions.append("logout")
        print(self.p1_actions)

        # Generate random sequence of actions for Player 2
        self.p2_actions = ACTIONS * NUM_ACTION_REPEATS
        random.shuffle(self.p2_actions)
        self.p2_actions.insert(0, "none")
        self.p2_actions.append("logout")
        print(self.p2_actions)

    
    """
    Called at the start of every turn to generate new values for player actions
    """
    def iterate(self):
        # Return True if we have finished going through all turns
        if self.cur_turn + 1 >= len(self.p1_actions):
            return True
        
        self.cur_turn += 1
    
        print(f"New P1 Action: {self.p1_actions[self.cur_turn]}")
        print(f"New P2 Action: {self.p2_actions[self.cur_turn]}")

        
        return False


    """
    Return both player expected actions in tuple of tuples: (p1_action,p2_action)
    """
    def get_correct_action(self):
        return self.p1_actions[self.cur_turn], self.p2_actions[self.cur_turn]


class Server(threading.Thread):
    def __init__(self, ip_addr, port_num, group_id):
        super(Server, self).__init__()

        # Setup logger
        self.log_filename = 'group{}_logs.csv'.format(group_id)
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        self.log_filepath = os.path.join(LOG_DIR, self.log_filename)
        self.columns = [
            'timestamp',
            'p1_action', 'gt_p1_action', 'p2_action', 'gt_p2_action',
            'response_time', 
            'is_p1_action_correct', 'is_p2_action_correct'
        ]
        self.df = pd.DataFrame(columns=self.columns)
        self.df = self.df.set_index('timestamp')

        # Setup turns
        self.turn_gen = TurnGenerator()                                                 # Initialize turn generator
        self.action_set_time = 0                                                        # Time turn instructions/actions were set by eval_server
        self.turn_wait_timeout = 60                                                     # Turn response timeout amount
        self.turn_wait_timer = threading.Timer(self.turn_wait_timeout, self.setup_turn) # Timer object to keep track of turn response timeout

        # Temporary storage for correct actions for each player
        self.last_p1_action = None
        self.last_p2_action = None

        # Ultra96 Connection things
        self.connection = None              # Ultra96 connection object
        self.has_no_response = False        # Flag set when there was no response from Ulra96
        self.logout = False                 # Flag for whether Ultra96 has triggered logout

        # Create a TCP/IP socket and bind to port
        self.shutdown = threading.Event()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip_addr, port_num)

        print('starting up on %s port %s' % server_address)
        self.socket.bind(server_address)


    """
    Main loop of server. This function performs a blocking wait for data from the Ultra96 until the Ultra96 
    disconnected. The data it receives is decrypted and is written to the logger. Lastly, the function sends
    the correct turn data (action) to the Ultra96 and sets up the next turn. 
    """
    def run(self):
        # Listen for incoming connections
        self.socket.listen(1)
        self.client_address, self.secret_key = self.setup_connection()      # Wait for secret key from Ultra96
        
        while not self.shutdown.is_set():           # Stop waiting for data if we received a shutdown signal from Ultra96
            data = self.connection.recv(1024)       # Blocking wait for data from the Ultra96

            if data:
                try:
                    msg = data.decode("utf8")                           # Decode raw bytes to UTF-8
                    decrypted_message = self.decrypt_message(msg)       # Decrypt message using secret key
                    
                    # If the action we received from the Ultra96 was a logout
                    if decrypted_message['p1_action'] == "logout":
                        self.logout = True
                        self.stop()

                    # If no valid action was sent
                    elif len(decrypted_message['p1_action']) == 0:
                        pass

                    # Received normal response from Ultra96. We log this response.
                    else:
                        self.has_no_response = False

                        # Store last action data for sending back to Ultra96 since self.setup_turn() overwrites data
                        correct_p1_action = self.last_p1_action
                        correct_p2_action = self.last_p2_action
                        
                        self.write_turn_to_logger(
                            decrypted_message['p1_action'],
                            correct_p1_action,
                            decrypted_message['p2_action'],
                            correct_p2_action
                        )

                    
                        print(f"Received: P1: {decrypted_message['p1_action']}, " + \
                            f"P2: {decrypted_message['p2_action']}")
                        print(f"Expected: P1: {correct_p1_action}, " + \
                            f"P2: {correct_p2_action}")
                        
                        self.setup_turn()                                   # Setup new turn to get new grid data
                        self.send_update(correct_p1_action, correct_p2_action)    # Send last action and new grid data to Ultra96 
                        
                except Exception as e:
                    traceback.print_exc()
            else:
                print('no more data from', self.client_address)
                self.stop()


    """
    This function waits for a connection from an Ultra96 and then reads the encryption key for the Ultra96's 
    messages from STDIN. Returns the encryption key and the Ultra96's port and IP address. 
    """
    def setup_connection(self):
        # print("No actions for 60 seconds to give time to connect")
        # self.timer = threading.Timer(self.timeout, self.set_next_action)
        # self.timer.start()

        # Wait for a connection
        print('Waiting for a connection')
        self.connection, client_address = self.socket.accept()

        print("Enter the secret key: ")
        secret_key = sys.stdin.readline().strip()

        print('connection from', client_address)
        if len(secret_key) == 16 or len(secret_key) == 24 or len(secret_key) == 32:
            p1_action, p2_action = self.turn_gen.get_correct_action()
            self.send_update(p1_action, p2_action)  # Send starting data to Ultra96
            self.setup_turn()
        else:
            print("AES key must be either 16, 24, or 32 bytes long")
            self.stop()
        
        return client_address, secret_key


    """
    This function executes every turn to set the actions for the 2 players.
    It first cancels the turn wait timer since the previous turn has ended and checks if we
    received a response from the Ultra96 in the previous turn.
    Next, it uses the TurnGenerator object to generate new actions and restarts
    the turn wait timer. 
    """
    def setup_turn(self):
        self.turn_wait_timer.cancel()
        if self.has_no_response:  # If no response was sent by Ultra96
            self.write_turn_to_logger("None", "None", "None", "None", "None", "None", "None", "None")
            print("TURN TIMEOUT")
            p1_action, p2_action = self.turn_gen.get_correct_action()
            self.send_update(p1_action, p2_action)  # Send turn state update even at timeout
        
        # Generate new actions using the TurnGenerator object
        # These generated values are read directly by Tkinter. 
        finished = self.turn_gen.iterate()
        # Check if no more turns left
        if finished:
            self.logout = True
            self.stop()

        # Get correct expected actions for checking once received Ultra96 response
        self.last_p1_action, self.last_p2_action = self.turn_gen.get_correct_action()

        # Used to calculate time taken to get response from Ultra96
        self.action_set_time = time.time()
        
        # Restart turn wait timer
        self.turn_wait_timer = threading.Timer(self.turn_wait_timeout, self.setup_turn)
        self.has_no_response = True
        self.turn_wait_timer.start()


    """
    This function decrypts the response message received from the Ultra96 using the secret encryption key
    that was entered in this script during initial connection by the Ultra96. 
    It returns an dictionary containing the action detected by the Ultra96. 
    """
    def decrypt_message(self, cipher_text):       
        decoded_message = base64.b64decode(cipher_text)                             # Decode message from base64 to bytes
        iv = decoded_message[:16]                                                   # Get IV value
        secret_key = bytes(str(self.secret_key), encoding="utf8")                   # Convert secret key to bytes

        cipher = AES.new(secret_key, AES.MODE_CBC, iv)                              # Create new AES cipher object
        decrypted_message = cipher.decrypt(decoded_message[16:]).strip()            # Perform decryption
        decrypted_message = decrypted_message.decode('utf8')                        # Decode bytes into utf-8

        decrypted_message = decrypted_message[decrypted_message.find('#'):]         # Trim to start of response string
        decrypted_message = bytes(decrypted_message[1:], 'utf8').decode('utf8')     # Trim starting # character

        messages = decrypted_message.split('|')         # Split parts of message by | token
        return {
            'p1_action': messages[0] , 'p2_action': messages[1]     
        }


    """
    Send last expected action to Ultra96.
    """
    def send_update(self, correct_p1_action: str, correct_p2_action: str):
        # Pack send data into a single string
        send_str = f"{correct_p1_action}|{correct_p2_action}"

        # Send without any encryption (unlike receiving)
        self.connection.sendall(send_str.encode())


    """
    Closes server upon end of assessment, after Ultra96 disconnects/sends logout message.
    """
    def stop(self):
        self.connection.close()
        self.shutdown.set()
        self.turn_wait_timer.cancel()
        print("bye bye")
        sys.exit()


    """
    Write data to logger. 
    """
    def write_turn_to_logger(self, 
            pred_p1_action: str, correct_p1_action: str, 
            pred_p2_action: str, correct_p2_action: str):

        log_filepath = self.log_filepath
        if not os.path.exists(log_filepath):  # first write
            with open(log_filepath, 'w') as f:
                self.df.to_csv(f)

        with open(log_filepath, 'a') as f:
            data = dict()
            data['timestamp'] = time.time()
            
            data['p1_action'] = pred_p1_action
            data['gt_p1_action'] = correct_p1_action
            data['p2_action'] = pred_p2_action
            data['gt_p2_action'] = correct_p2_action

            data['response_time'] = data['timestamp'] - self.action_set_time
            data['is_p1_action_correct'] = (pred_p1_action == correct_p1_action)
            data['is_p2_action_correct'] = (pred_p2_action == correct_p2_action)
            
            self.df = pd.DataFrame(data, index=[0])[self.columns].set_index('timestamp')
            self.df.to_csv(f, header=False)



def main():
    if len(sys.argv) != 4:
        print('Invalid number of arguments')
        print('python3 eval_server.py [IP address] [Port] [groupID]')
        sys.exit()

    ip_addr = sys.argv[1]
    port_num = int(sys.argv[2])
    group_id = sys.argv[3]

    server = Server(ip_addr, port_num, group_id)
    server.start()

    # Initialize base window
    display_window = tk.Tk()
    display_window.title = "Evaluation Server"
    main_frame = tk.Frame(
        display_window
    )
    main_frame.pack(expand=True, fill='both')

    # Finished turns
    turn_text = tk.StringVar()
    turn_label = tk.Label(main_frame, textvariable=turn_text, font=("times", 80))
    turn_label.pack(fill='x')

    # Player 1 column
    p1_frame = tk.Frame(main_frame, bg="red")
    p1_frame.pack(expand=True, fill='both', side='left')
    # Player 1 title
    p1_label = tk.Label(p1_frame, text="Player 1", font=('times', 100, 'bold'), bg="red")
    p1_label.pack(ipady=20)
    # Player 1 variable frame
    p1_var_frame = tk.Frame(p1_frame, bg='#ffcccb')
    p1_var_frame.pack(expand=True, fill='both')
    # Player 1 action variable
    p1_action_text = tk.StringVar()
    p1_action_label = tk.Label(p1_var_frame, textvariable=p1_action_text, font=("times", 100), bg='#ffcccb')
    p1_action_label.pack(expand=True)
    # Player 2 variable separator
    p1_var_sep = ttk.Separator(p1_var_frame, orient=HORIZONTAL)
    p1_var_sep.pack(expand=True, fill='x')

    # Player 2 column
    p2_frame = tk.Frame(main_frame, bg="blue")
    p2_frame.pack(expand=True, fill='both', side='right')
    # Player 2 title
    p2_label = tk.Label(p2_frame, text="Player 2", font=('times', 100, 'bold'), bg="blue")
    p2_label.pack(ipady=20)
    # Player 2 variable frame
    p2_var_frame = tk.Frame(p2_frame, bg='#add8e6')
    p2_var_frame.pack(expand=True, fill='both')
    # Player 2 action variable
    p2_action_text = tk.StringVar()
    p2_action_label = tk.Label(p2_var_frame, textvariable=p2_action_text, font=("times", 100), bg='#add8e6')
    p2_action_label.pack(expand=True)
    # Player 2 variable separator
    p2_var_sep = ttk.Separator(p2_var_frame, orient=HORIZONTAL)
    p2_var_sep.pack(expand=True, fill='x')    

    # Player column separator
    col_sep = ttk.Separator(main_frame, orient=VERTICAL)
    col_sep.pack(expand=True, fill='y')
    
    # Update window based on data in server
    display_window.update()
    while not server.shutdown.is_set():
        turn_text.set(f"{server.turn_gen.cur_turn} / {len(server.turn_gen.p1_actions)-1}")
        
        p1_action_text.set(server.turn_gen.get_correct_action()[0])
        p2_action_text.set(server.turn_gen.get_correct_action()[1])

        display_window.update()
        time.sleep(0.2)


if __name__ == '__main__':
    main()


