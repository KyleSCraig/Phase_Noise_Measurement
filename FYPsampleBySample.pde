import processing.net.*;
//import Arrays;
Client myClient;
int dataIn;
int plotBufferx = -1;
int plotBuffery[]= {-1,-1,-1,-1,-1,-1,-1};
int inV = 0;
int inT = 0;
int inTold = 0;
int inVold = 0;
int time[] = new int[100]; //parametrise!!!
int nt = 0;
char Brightness = 67;
char Saturation = 67;
char RED[] = {0,Saturation,Brightness};
char GREEN[] = {120,Saturation,Brightness};
char BLUE[] = {240,Saturation,Brightness};
char HUES[] = {0,120,240,0,120,240};
char SATS[] = {67,67,67,33,33,33};
char BRIS[] = {67,67,67,33,33,33};
final String DIR = "/home/pi/Downloads/";
String filename;
int readLine = 0;

void setup(){
  size(800,800);
  background(255);
  //printArray(SPI.list());
  rectMode(CORNER);
  //println(time);
  colorMode(HSB, 360, 100, 100);
  myClient = new Client(this, "127.0.0.1",65432);
}


void draw(){
  
  for (int a=0; a<15;a++){
    String dataLine = "";
    while(true){
      if(myClient.available()>0){
        dataIn = myClient.read();
      }
      if(dataIn==10){
        break;
      } else {
        dataLine = dataLine+char(dataIn);
      }
    }
    if(dataLine!=""){
      dataLine = dataLine.replaceAll("[\\[\\]\\s]","");
      //println(dataLine);
      int newData[] = int(split(dataLine,','));
      //println(newData);
      plot(newData,RED);
    }
  }
  //println(newData);
  noStroke();
  fill(0,0,100);
  rect((plotBufferx+1)%width,0,100,height);
  //stroke(0,100,0);
  //line((plotBufferx+1)%width,height-220,(plotBufferx+1)%width+100,height-220);
}


void plot(int[] y,char[] colour){
  
  strokeWeight(1);
  int xOff = width*int(y[0]/width); //if effective width is changed this needs to reflect that
  //stroke(colour[0],colour[1], colour[2]);
  for (int a=0; a<6; a++){
    //print(x[a]);
    //println(y[a]);
    stroke(HUES[a],SATS[a],BRIS[a]);
    if(y[0]-plotBufferx<5){
      line(plotBufferx-xOff,height/2-plotBuffery[a+1]-0*220,y[0]-xOff,height/2-y[a+1]-0*220);
    }
    
    plotBuffery[a+1] = y[a+1];
  }

  plotBufferx = y[0];
    
}
