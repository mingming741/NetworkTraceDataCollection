// Client side C/C++ program to demonstrate Socket programming
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>

#define PORT 7777
#define LOCAL_HOST "127.0.0.1"
#define HOST "192.168.80.122"
#define MM_SERVER_ADD "100.64.0.1"
#define MM_CLIENT_ADD "100.64.0.2"

int main(int argc, char const *argv[])
{
  int sock = 0;
  struct sockaddr_in serv_address;
  if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0){
    printf("\n Socket creation error \n");
    return -1;
  }

  serv_address.sin_family = AF_INET;
  serv_address.sin_port = htons(PORT);

  // Convert IPv4 and IPv6 addresses from text to binary form
  if(inet_pton(AF_INET, MM_SERVER_ADD , &serv_address.sin_addr)<=0){
    printf("\nInvalid address/ Address not supported \n");
    return -1;
  }

  if (connect(sock, (struct sockaddr *)&serv_address, sizeof(serv_address)) < 0)
  {
    printf("\nConnection Failed \n");
    return -1;
  }

  int valread, i;
  char buffer[1024] = {0};
  char *message = "Client Message";
  for(i = 0; i < 3; i++){
    send(sock, message, strlen(message), 0);
    //valread = read(sock, buffer, 1024);
    //printf("%s\n",buffer);
  }
  return 0;
}
