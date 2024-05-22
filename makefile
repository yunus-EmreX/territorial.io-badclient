
CC = gcc

CFLAGS = -Wall -Wextra -g

SRC = main.c websocket.c util.c

OBJ = $(SRC:.c=.o)

EXEC = project

all: $(EXEC)


$(EXEC): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJ) $(EXEC)
