For use docker.
1) Install Xming server
2) Restart the PC
3) Go to console in directory where Xming was installed:
command: Xming.exe -ac
4) Go to docker console:
command: docker pull jlzk551/stegoapp:v1.0
5)Then watch your ipv4 in Ethernet adapter Ethernet with ipconfig command
6)From console type
command: set DISPLAY=ip_from_previous_step:0.0
7)command: docker run -it --rm -e DISPLAY=%DISPLAY% --network="host" --name your_container_name jlzk551/stegoapp
8)The application will run in Xming