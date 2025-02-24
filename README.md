It is a programming realization of steganographic method with code control with blind decoding. 
Written on python.
Embedding additional information in the image:
1.	The image is divided into blocks  16X16.
2.	2.	A code word multiplied by a bit of additional information is added to each block.
stegan message block will then be as follows:
Mi= Xi+(-1)^di*T16, where  Xi is the block of the original image.
di — bit of additional information;
T16 — code word.
To extract additional information, you need to perform the following steps:
1.	We divide the stegan message block into 16 parts
M=[mu11 mu12 mu13 mu14;
mu21 mu22 mu23 mu24;
mu31 mu32 mu33 mu34;
mu41 mu42 mu43 mu44],
where muij is a subblock 4*4 block 16*16.
2.	We will get 8 vectors  u , by element-by-element multiplication  on code words T41 and T42
3.	We subtract their average value from the vectors  u, obtaining vectors y
4. We restore a bit of additional information: biti=sign(sum(yk_1*structure)+sum(yk_2*structure))
   where k=1,2,3,4; structure=[1 1 -1 -1];
   We summarize all biti that is biti!=0 (  bit3 and bit4 multiply by -1 ) .
If the sum biti is nonzero, then we take bit=sign(sum(biti)) . Otherwise, we construct the vector bits=[bit1 bit2 bit3 bit4] . We count in how many positions it coincides with the structures StructurePOSITIVE=[1 1 -1 -1], StructureNEGATIVE=[-1 -1 1 1]  if the number of coincidences of the vector with positions StructurePOSITIVE>StructureNEGATIVE , then bit=1  otherwise bit=-1 .

   Algorithm of extraction(https://github.com/user-attachments/assets/ff6ef7b2-36b0-4645-aa5f-ba0da2522de2)


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


