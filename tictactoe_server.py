import socket
import threading
import time

# Creating a server class
class TicTacToeServer:
    def __init__(self):
        self.localHost = 'localhost'
        self.localPort = 8000
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.localHost, self.localPort))
        self.server_socket.listen(2)
        self.connectedClients = []
        self.game_board = [' ',' ',' ',' ',' ',' ',' ',' ',' ']
        self.current_player = 0
        self.players = 0
        self.status = 0
        self.client_table = {}

        # Wait for a connection
        print('Waiting for a connection...')
        while len(self.connectedClients) != 2:                 
            connection, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target = self.handle_client,args=(connection, client_address))
            client_thread.start()
            time.sleep(0.2)
                      
            
    # this method handls each client connection
    def handle_client(self, client_socket, addr):
        print(f"New connection from {addr}")
        #print(client_socket)   
        
        self.connectedClients.append(client_socket)
        if len(self.connectedClients) == 1:
            self.client_table[addr[1]] = 'player 1'
            client_socket = self.connectedClients[0]
            data = 'Welcome to Tic-Tac-Toe!\nYou are player 1 [X]\n'            
            client_socket.send(self.encryption(data,1).encode())

        if len(self.connectedClients) == 2:
            self.client_table[addr[1]] = 'player 2'            
            client_socket = self.connectedClients[1]
            self.current_player = 1
            data = 'Welcome to Tic-Tac-Toe!\nYou are player 2 [O]\n'
            client_socket.send(self.encryption(data,2).encode())
            self.current_player = 0
            
            time.sleep(0.2)
            print("\nClient Table:")
            print("Client name\tPort Number")
            for i in self.client_table:
                print(self.client_table[i],"\t",str(i))
            print()
            self.play_game()
            self.connectedClients = []
            time.sleep(0.2)
            print('Game Over!!')
            exit() 
        else:
            data = 'Waiting for another player...\n'
            client_socket.send(self.encryption(data,self.current_player+1).encode())
        

    #play_game() method is responsible for controlling the game flow
    def play_game(self):
        print("Game started!") 
        print(self.display_board())       
        while not self.game_over():   
            self.play_turn()
        
        client_socket = self.connectedClients[1-self.current_player]
        #self.current_player = 1-self.current_player
        if(self.current_player == 0):
            des = 2
        else:
            des = 1
        if self.check_win():   
            self.status == 1   
            winner = self.current_player + 1            
            sendWinner = '\nPlayer '+str(winner)+' wins'
            client_socket.send(self.encryption(sendWinner,des).encode())
            self.send_to_all_clients(f'close')
        else:
            self.status == 1
            tie = '\nTie game.'
            client_socket.send(self.encryption(tie,des).encode())
            self.send_to_all_clients(f'close')
        self.reset_game()

    #play_turn() method is responsible for getting the player's move and updating the game board
    def play_turn(self):
        while 1:
            client_socket = self.connectedClients[self.current_player]
            playerdata = '\nPlayer '+str(self.current_player+1)+' turn.'
            if self.current_player == 0:
                playerdata = playerdata+' [X]'
            else:
                playerdata = playerdata+' [O]'

            client_socket.send(self.encryption(playerdata,self.current_player+1).encode())
            
            move = client_socket.recv(1024).decode()
            
            if(move == None):
                self.play_turn()
           
            if self.game_board[int(move)] != ' ':
                data = 'The location is already filled!, please select another move.\n'
                client_socket.send(self.encryption(data,self.current_player+1).encode())
            else:
                break
        self.update_board(move)
        client_socket.send(self.encryption(self.display_board(),self.current_player+1).encode())
        if self.check_win():
            return
        if self.check_tie():
            return
        self.current_player = 1 - self.current_player

    #this method is responsible for updating the game board with the current player's move.
    def update_board(self, move):
        move = int(move)
        if self.current_player == 0:
            self.game_board[move] = 'X'
        else:
            self.game_board[move] = 'O'

    #check_win method is responsible for checking if the current player has won the game by checking all possible winning combinations.
    def check_win(self):
        winning_combinations = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6]
        ]
        for combo in winning_combinations:
            if self.game_board[combo[0]] == self.game_board[combo[1]] == self.game_board[combo[2]] != ' ':
                return True
        return False

    #check_tie method checks if the game is tied by checking if there are any empty spaces left on the board.
    def check_tie(self):
        if ' ' not in self.game_board:
            return True
        return False

    #game_over method checks if the game is over by calling check_win() and check_tie() methods.
    def game_over(self):
        return self.check_win() or self.check_tie()

    #reset_game() method is called after the game is over to reset the game board and the current player.
    def reset_game(self):
        self.game_board = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
        self.current_player = 0

    #display_board() method is responsible for formatting and displaying the game board to the players.
    def display_board(self):
        board = '\n\t0\t1\t2'
        next = 0
        for i, val in enumerate(self.game_board):
            if i % 3 == 0 and next<= 2:
                board += '\n'+str(next)+' '
                next += 1
            board += f'\t{val} '
        return board

    #send_to_all_clients method is responsible for sending messages to all clients connected to the server.
    def send_to_all_clients(self, message):
        player = 1
        for client_socket in self.connectedClients:
            client_socket.send(self.encryption(message,player).encode())
            player = 2

    #encryption method is used for encrypting the data with sourse and destination
    def encryption(self,data,destination):
        d = data
        data = 'S:'+str(destination)+':'+str(len(d))+":"+str(data)
        return data

#PlayerNode class is responsible for players to connect to the server.
class PlayerNode:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 8000))
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()
        self.game_board = [' ',' ',' ',' ',' ',' ',' ',' ',' ']
        self.playernumber = -1

    #this method is used for receiving messages from the server
    def receive_messages(self):
        while True:
            message = self.client_socket.recv(1024).decode()
            message = self.decryption(message)   

            if message == None:
                continue         
            if 'You are' in message:
                self.playernumber = int(str(message[39]))
                print(message)
            
            elif 'updatedBoard' in message:
                print(message)
                print("in updated board")
                self.modifyboard(message)
                print(self.game_board)

            elif 'close' in message:
                self.client_socket.close()
                break
            else:
                print(message)
            

            if 'turn' in message:
                while 1:
                    move = input('Enter your move (0-8): ')
                    if move not in ['1','2','3','4','5','6','7','8','0']:
                        print('Please enter the move within limit(0-8).\n')
                    else:
                        self.client_socket.send(move.encode())
                        break
                       
    ## this method is used for modifying the game board
    def modifyboard(self,board):
        board = board.replace('[','')
        board = board.replace(']','')
        board = board.replace("'",'')
        board = board.replace('updatedBoard','')
        board = board.split(",")
        print(board)
        self.game_board = board

    # this method is used for decrypting the message received from the server
    def decryption(self,data):        
        if(len(data) == 0):
            return None
        newdata = data.split(':') 
        if(newdata[0] == 'S'):
            data1 = newdata[3]
            if (int(newdata[1]) == self.playernumber or self.playernumber == -1):
                if(self.playernumber == -1):
                    self.playernumber = newdata[1]
                if(int(newdata[2]) == len(data1)):
                    return data1

    

#Creating a main class
def main():

    server = threading.Thread(target=TicTacToeServer) # creating thread for server
    player1 = threading.Thread(target=PlayerNode) # creating thread for player 1
    player2 = threading.Thread(target=PlayerNode) # creating thread for player 2

    # starting the 1 server and 2 players
    server.start()
    player1.start()
    player2.start()
     
    player1.join()
    player2.join()

if __name__ == '__main__':
    main()