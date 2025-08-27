This project outlines a C2 (Command and Control) framework from scratch. Utalizing a python based server, a user can send commands and execute them to hosts that are running the implant.


## Implant
The implant is created in C++ and is a template for what a real life implant could look like. It searches for the listening server and constantly asks for tasking while updating previous task results

## User Interface
This is a simple GUI that connects to the listen server to send commands to implants. This is currently a very simple gui written completely in python.

## Listen Server
The listen server is in charge of sending tasking to the implants, received from the user interface.

## Future Plans
- List all implants in the GUI
- Improve GUI and move away from Python GUI implementation
- Create more templates in the Implant
