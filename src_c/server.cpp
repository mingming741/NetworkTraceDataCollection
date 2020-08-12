// Server side C/C++ program to demonstrate Socket programming
#include <unistd.h>
#include <stdio.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>

#define PORT 7777
#define LOCAL_HOST "127.0.0.1"
#define SERVER_ADDR "192.168.80.77"

int main(int argc, char const *argv[])
{
    int server_fd, new_socket_fd;

    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
      perror("socket failed");
      exit(EXIT_FAILURE);
    }

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
      perror("setsockopt");
      exit(EXIT_FAILURE);
    }

    // Forcefully attaching socket to the port 8080
    struct sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(PORT);
    inet_pton(AF_INET, SERVER_ADDR, &server_address.sin_addr); // convert IPv4 and IPv6 addresses from text to binary form

    if (bind(server_fd, (struct sockaddr *)&server_address, sizeof(server_address)) < 0) { // 将sockaddr_in cast成了一个sockaddr
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 3) < 0){
      perror("listen");
      exit(EXIT_FAILURE);
    }

    char LocalAddress[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &(server_address.sin_addr), LocalAddress, INET_ADDRSTRLEN);
    printf("Server Listen at Address %s, Port %d\n", LocalAddress, (int)ntohs(server_address.sin_port));


    struct sockaddr_in client_address;
    int addrlen = sizeof(client_address);
    if ((new_socket_fd = accept(server_fd, (struct sockaddr *)&client_address, (socklen_t*)&addrlen))<0) {
      perror("accept");
      exit(EXIT_FAILURE);
    }
    else{
      char clientAddress[INET_ADDRSTRLEN];
      inet_ntop(AF_INET, &(client_address.sin_addr), clientAddress, INET_ADDRSTRLEN);
      printf("Server Connect Client, Address %s, Port %d\n", clientAddress, (int)ntohs(client_address.sin_port));
    }

    int valread;
    char buffer[1024] = {0};

    char *message = "Server ACK";
    while(1){
      valread = recv(new_socket_fd, buffer, 1024);
      //printf("%s\n",buffer);
      send(new_socket_fd, message, strlen(message), 0);
    }
}
