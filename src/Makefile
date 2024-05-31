.PHONY: clean

all: messages_pb2.py
	@echo Build successfully

clean:
	rm -f *_pb2.py
	@echo Clean successfully

messages_pb2.py: messages.proto
	protoc --python_out=. $<