import processing.net.*;
Client myClient;
int offX = 160;
int offY = 70;
int displayMode = 1;
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
  //printArray(SPI.list()); //can be run to help if the SPI used isn't 0
  rectMode(CORNER);
  colorMode(HSB, 360, 100, 100);
  myClient = new Client(this, "127.0.0.1",65432);
}

void draw(){
  if(displayMode==255){ //oscilloscope mode setup
    background(0,0,100);
    strokeWeight(2);
    stroke(0,100,0);
    fill(0,100,0);
    line(offX-2,-offY+height-360,offX-2,-offY+height);
    line(offX,-offY+height+2,offX+height,-offY+height+2);
    textAlign(CENTER,TOP);
    text("time",width/2,height-offY);
    textAlign(RIGHT,CENTER);
    text("120",width/2-height/2-2,height-offY-60);
    text("240",width/2-height/2-2,height-offY-120);
    text("360",width/2-height/2-2,height-offY-180);
    text("480",width/2-height/2-2,height-offY-240);
    text("600",width/2-height/2-2,height-offY-300);
    displayMode=1;
  } else {
    
    for (int a=0; a<15;a++){ //does 15 points per screen refresh because the points are coming in faster than 60 fps
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
        dataLine = dataLine.replaceAll("[\\[\\]\\s]",""); // removes all "[", "]", and " "
        //println(dataLine);
        int newData[] = int(split(dataLine,','));
        //println(newData);
        if(displayMode==0){ // plot unit circle mode
          if(a==0){
            background(0,0,100);
            stroke(0,100,0);
            strokeWeight(2);
            fill(0,0,100);
            ellipse(width/2,height/2,height*2/3,height*2/3);
            line(width/2,0,width/2,height);
            line(width/2-height/2,height/2,width/2+height/2,height/2);
            noStroke();
            
            fill(0,20,80);
            ellipse(width/2+height/3*cos(radians(newData[4])/10),height/2-height/3*abs(sin(radians(newData[4])/10)),50,50);
            //ellipse(width/2+width/3*cos(radians(newData[1])),height/2-height/3*sin(radians(newData[1])),10,10);
            fill(120,20,80);
            ellipse(width/2+height/3*cos(radians(newData[5])/10),height/2-height/3*abs(sin(radians(newData[5])/10)),50,50);
            //ellipse(width/2+width/3*cos(radians(newData[2])),height/2-height/3*sin(radians(newData[2])),10,10);
            fill(240,20,80);
            ellipse(width/2+height/3*cos(radians(newData[6])/10),height/2-height/3*abs(sin(radians(newData[6])/10)),50,50);
            //ellipse(width/2+width/3*cos(radians(newData[3])),height/2-height/3*sin(radians(newData[3])),10,10);
            
            fill(0,67,67);
            ellipse(width/2+height/3*cos(radians(newData[1])/10),height/2-height/3*sin(radians(newData[1])/10),50,50);
            //ellipse(width/2+width/3*cos(radians(newData[1])),height/2-height/3*sin(radians(newData[1])),10,10);
            fill(120,67,67);
            ellipse(width/2+height/3*cos(radians(newData[2])/10),height/2-height/3*sin(radians(newData[2])/10),50,50);
            //ellipse(width/2+width/3*cos(radians(newData[2])),height/2-height/3*sin(radians(newData[2])),10,10);
            fill(240,67,67);
            ellipse(width/2+height/3*cos(radians(newData[3])/10),height/2-height/3*sin(radians(newData[3])/10),50,50);
            
    
          }
        } else if(displayMode==1){ plot oscilloscope mode
          plot(newData,RED);
        }
        //plot(newData,RED);
      }
    }
    //println(newData);
    if(displayMode==1){
      noStroke();
      fill(0,0,100);
      rect(offX+(plotBufferx+1)%height,0,100,height-offY);
    }
  }
}


void plot(int[] y,char[] colour){
  
  strokeWeight(1);
  int xOff = height*int(y[0]/height); //if effective width is changed this needs to reflect that
  //int yOff; 
  //stroke(colour[0],colour[1], colour[2]);
  for (int a=0; a<3; a++){
    
    //print(x[a]);
    //println(y[a]);
    stroke(HUES[a],SATS[a],BRIS[a]);
    if(abs(y[0]-plotBufferx)<5){
      line(plotBufferx-xOff+offX,-offY+height-plotBuffery[a+1]/10/2,y[0]-xOff+offX,-offY+height-y[a+1]/10/2);
    }
    
    plotBuffery[a+1] = y[a+1];
  }

  plotBufferx = y[0];
    
}

void mousePressed() {
  if(displayMode==1){
    displayMode = 0;
  } else if(displayMode==0){
    displayMode = 255;
    redraw();
    //displayMode = 1;
  }
}
