#!/usr/bin/python
from PIL import Image, ImageDraw, ImageFont
import csv
import numpy

######################################################################
######################modify variables here ##########################
######################################################################
title = '3CYT'
ColumnOffset=0
RowOffset=0
ColumnSpacing=0.0003 # spot spacing (meters)
RowSpacing=0.0003
StartColumn_mm=2
StartRow_mm=2
PinType='946MP4'
PinCol=1 #where the pin is located
PinRow=1
Slides=1 #number of slides
SlideNo=7 #where to start counting slides (7 is top left corner)
Arrays=10 #arrays per slide
Array=1 #array on which to start
PrintSpots = 61 # number of spots to print at a time
ArrayOffsetHorizontal_mm=1 #space between arrays (last spot to first spot) 
ArrayOffsetVertical_mm=1 #space between arrays (last spot to first spot) 
WashFreq=100 #wash after this no of prints using the same sample
PreprintSpots=25 # if preprint required
PreprintSlide=7 #preprint area can be on the same slide
PreprintTime=0.1
PreprintStartColumn_mm=50 #area in wich to start preprinting
PreprintStartRow_mm=5
#wash times and number of washes
WashTime=0.5
DryTime=0.5
FinalWashTime=2
FinalDryTime=10
NbrWashes=2
SampleTime=3 #time to load the sample
PrintTime=0.1 #sample print time
#variables for drawing plate and arrays; no impact on phisical arrays
platePPW=25 #pixels per well
wellRadius=platePPW/2
spotRadius=int(round(ColumnSpacing*10**5))/2 #1mm=100px, 10um/px
arrayPPmm=100 #pixels per mm
well='A0'



############################################all text strings required for generating the spo file############
################################################################################################################
################################################################################################################
###############################################################################################################
#############################################################################################################
header = '<Procedure xmlns="http://www.korteks.com/spotbot/"><Version>1.1</Version><Title>'+title+'</Title><SlideOriginOffset><ColumnOffset>'+str(ColumnOffset)+'</ColumnOffset><RowOffset>'+str(RowOffset)+'</RowOffset></SlideOriginOffset><SpotSpacing><ColumnSpacing>'+str(ColumnSpacing)+'</ColumnSpacing><RowSpacing>'+str(RowSpacing)+'</RowSpacing></SpotSpacing><ZAxisInhibit>False</ZAxisInhibit><Lights><Power>True</Power><Blink>No</Blink></Lights><PinLoad><Type>'+PinType+'</Type><Column>'+str(PinCol)+'</Column><Row>'+str(PinRow)+'</Row></PinLoad><Lights><Power>False</Power><Blink>No</Blink></Lights>'



def sampleComment(sampleName, well, NoSpots, arrayNo):
        SampleComment = '<Comment>Process sample '+sampleName+' from Well '+well+' for a total of '+str(NoSpots)+' spots on Array '+str(arrayNo)+' </Comment>'
        return SampleComment


wash = '<Wash><Time>'+str(WashTime)+'</Time></Wash><Dry><Time>'+str(DryTime)+'</Time></Dry>'

FinalWash = '<Wash><Time>'+str(FinalWashTime)+'</Time></Wash><Dry><Time>'+str(FinalDryTime)+'</Time></Dry>'



def getSample(sampleNumber, column, row):
	sampleNumber=1
        GetSample = '<GetSample><Number>'+str(sampleNumber)+'</Number><Column>'+str(column)+'</Column><Row>'+str(row)+'</Row><Time>'+str(SampleTime)+'</Time></GetSample>'
        return GetSample



def prePrint(Slide, Column, Row):
            PrePrint =  '<SpotSlide><Number>'+str(Slide)+'</Number><Column>'+str(Column)+'</Column><Row>'+str(Row)+'</Row><Time>'+str(PreprintTime)+'</Time></SpotSlide>'
            return PrePrint



def printSpot(Slide, Column, Row):
            PrintSpot =  '<SpotSlide><Number>'+str(Slide)+'</Number><Column>'+str(Column)+'</Column><Row>'+str(Row)+'</Row><Time>'+str(PrintTime)+'</Time></SpotSlide>'
            return PrintSpot

footer = '<Lights><Power>False</Power><Blink>No</Blink></Lights></Procedure>'
############################ scan the array configuration####################
###########################################################################
###########################################################################
array = Image.new("RGB", (25*arrayPPmm, 75*arrayPPmm), "White")
arrayL = list(csv.reader(open("array.csv")))
arrayLRows = sum(1 for row in arrayL)
arrayLCols=len(arrayL[0])
drawArray = ImageDraw.Draw(array)

#########################scan the plate configuration#####################
########################################################################
#########################################################################
plate = Image.new("RGB", (25*platePPW,17*platePPW), "white") # load plate and draw leaving space for text border
plateL = list(csv.reader(open("plate.csv")))
plateLRows = sum(1 for row in plateL)
plateLCols=len(plateL[0])
plateColNames=plateL[0][1:] # get col names
drawPlate = ImageDraw.Draw(plate) # plate for drawing

#################################calculate extra variables##################
##########################################################################
###########################################################################
ArraySize=(arrayLRows, arrayLCols)
StartColumn=int(round(StartColumn_mm/(ColumnSpacing*10**3))) #Calculate rows and columns for spacing 
StartRow=int(round(StartRow_mm/(RowSpacing*10**3)))
ArrayOffsetHorizontal=int(ArrayOffsetHorizontal_mm/(ColumnSpacing*10**3)) + ArraySize[1] # calculate spacing
ArrayOffsetVertical=int(ArrayOffsetVertical_mm/(ColumnSpacing*10**3)) + ArraySize[0]
PreprintStartColumn=PreprintStartColumn_mm/ColumnSpacing #area in wich to preprint
PreprintStartRow=PreprintStartRow_mm/(RowSpacing*10**3) #same thing
PreprintCurrentColumn=PreprintStartColumn #variables to keep track of preprint position
PreprintCurrentRow=PreprintStartRow
PreprintLimit=round(0.025/ColumnSpacing)-10 #do not preprint off the slide :)
ArrayMaxPrintHorizontal = int((0.025/ColumnSpacing)-ArrayOffsetHorizontal-StartColumn) #############################################################modified and untested 26_10_2015
ArrayMaxPrintVertical = int(round(0.075/ColumnSpacing-PreprintStartRow))
###### create slide number sequence
slides = list()
for slide in range(0, Slides):
        slides = slides + [SlideNo+slide]


arrays = list()
for singlearray in range(Array-1, Arrays):
        arrays = arrays + [Array-1+singlearray]




##########################################process plate and array information ######################333
##################################################################################################33
#####################################################################################################
######################################################################################################
# get row names
plateRowNames = list() 
for i in range(1, plateLRows): 
    plateRowNames.append(plateL[i][0])
plateRowNames.sort()
# get sample names
sampleNames = list()
for i in range(1, plateLRows):
        for a in range(1,len(plateL[i])):
                if  plateL[i][a] != '':
                        sampleNames.append(plateL[i][a])
sampleNames.sort()

# get index of sample names in plate and assign an unique colour (10 is the limit of available colours)
col = (0,256,0)
blu = 1
samples = list()
for sample in sampleNames:
	blu = blu+1
        col=tuple(map(sum,zip(col,(5,-5,0))))
        for row in range(0, plateLRows):
                try: 
                        samples.append((sample, row, plateL[row].index(sample), col))
                except ValueError:
                        print 
                        #sort samples    
samples.sort(key=lambda tup: tup[1])
print "Sample positions:", samples



# take samples in order and search for their positions on the array
# assign a speciffic color to each sample respocting the same colors from plate
arrayConf = list()
for sample in sampleNames:
        SamplePlate = [elem for elem in samples if sample in elem]
        col = SamplePlate[0][3]
        PlateRow = SamplePlate[0][1]
        PlateCol = SamplePlate[0][2]
        for row in range(0, arrayLRows):
                try:
                        for i, item in enumerate(arrayL[row]):
                                if item == sample:
                                        arrayConf.append((sample, i, row, col, PlateCol, PlateRow))
                except ValueError:
                        print 
                        


arrayConf.sort(key=lambda tup: tup[0])
print "array configuration", arrayConf
print "SampleNames", sampleNames


print "Plate Rows x Cols", plateLRows, plateLCols
print "array Rows x Cols", ArraySize[0], ArraySize[1] #arrayLRows, arrayLCols

###############################################################
################################################################
##############################################################
################################################################

#function for generating positions (rows vs columns)
def conf2grid(dotCoord):
        row=dotCoord[1]+StartRow
        column=dotCoord[2]+StartColumn
        arrayGrid.append((dotCoord[0], row, column, dotCoord[3], dotCoord[4], dotCoord[5]))
        #print "start", StartRow, StartColumn
        return

arrayGrid = list()
for dot in range(0, len(arrayConf)):
    conf2grid(arrayConf[dot])

print "array Grid:", arrayGrid
#function for generating the grid of arrays
tableOfArrays = list()
Hpoz = 0
Vpoz = 0
for singlearray in range(0, Arrays):
        if StartColumn+ArrayOffsetHorizontal*Hpoz+ArraySize[1] <= ArrayMaxPrintHorizontal:
                tableOfArrays.append((Hpoz,Vpoz))
                Hpoz += 1
        else:
            if StartRow+ArrayOffsetVertical*Vpoz+ArraySize[0] <= ArrayMaxPrintVertical:
                tableOfArrays.append((Hpoz, Vpoz))
                Vpoz += 1
                Hpoz = 0
print "herehere", tableOfArrays
# function for shifting array replicates
shiftRows=0
shiftColumns=0
def arrayShift(arrayTemplate, singlearray):
        print "ArrNo", singlearray
        global shiftRows
        global shiftColumns
        #print "maxH", ArrayMaxPrintHorizontal
        #print "maxV", ArrayMaxPrintVertical
        shiftColumns=int(ArrayOffsetHorizontal*100*tableOfArrays[singlearray-1][0])/100
        print "HorizOffset", shiftColumns
        shiftRows=int(ArrayOffsetVertical*100*tableOfArrays[singlearray-1][1])/100
        print "VerticalOffset", shiftRows
        if singlearray == 1:
                shiftRows = 0
                shiftColumns = 0 
        for row, Row in enumerate(arrayTemplate):
            arrayTemplate[row][1] = arrayTemplate[row][1]+shiftColumns
            arrayTemplate[row][2] = arrayTemplate[row][2]+shiftRows 
        return arrayTemplate

# function for plotting the plate
################################################################
###################################################################
#######################################################################
##########################################################################
fontArial = ImageFont.truetype("Arial.TTF", platePPW)
#draw row names
RowTxt = platePPW
RowTxtX= platePPW
for item in plateRowNames:
        #print item
        drawPlate.line((0.50*platePPW, RowTxt-0.05*platePPW, 10000, RowTxt-0.05*platePPW), fill="green", width=int(0.05*platePPW))
        drawPlate.text((0.05*platePPW,RowTxt), item, font=fontArial, fill=1)
        RowTxt=RowTxt+platePPW
        RowTxtY=RowTxtX+platePPW
#draw column names
RowTxt = platePPW
RowTxtX= platePPW
fontArial = ImageFont.truetype("Arial.TTF", int(0.80*platePPW))
for item in plateColNames:
        #print item
        drawPlate.line((RowTxtX - 0.05*platePPW, 0.5*platePPW, RowTxtX - 0.05*platePPW, 10000 ), fill="green", width=int(0.05*platePPW))
        drawPlate.text((RowTxtX, 0.05*platePPW), item, font=fontArial, fill=1)
        RowTxt=RowTxt+platePPW
        RowTxtX=RowTxtX+platePPW
# draw samples
fontArial = ImageFont.truetype("Arial.TTF", int(0.4*platePPW))
for sample in samples:
        sRow = sample[2]*platePPW
        sCol = sample[1]*platePPW
        sName = sample[0]
        sColr = sample[3]
        drawPlate.ellipse((sRow, sCol, sRow+wellRadius*2-0.05*platePPW, sCol+wellRadius*2-0.05*platePPW), fill=sColr)
        drawPlate.text((sRow,sCol), sName, font=fontArial, fill=1)
       # print sample[0]



################################### all output to file is generated here ##############################
# convert array indexes to rows and columns
# if multiple arrays are necessary create them now


#first open file as w, thereby deleting previous contents

output = open(title+'.xml', "w")
            
output.write(header)

output = open(title+'.xml', 'a')

output.write(wash*NbrWashes)

#function for plotting array and appending lines to text file
################################################################
############################################################
##############################################################
tiemp = list()
def plotDot(dotGrid):
    xStart = dotGrid[1]*(RowSpacing*10**3)*100  + spotRadius
    yStart = dotGrid[2]*(RowSpacing*10**3)*100  + spotRadius
    xEnd = dotGrid[1]*(RowSpacing*10**3)*100 - spotRadius
    yEnd = dotGrid[2]*(RowSpacing*10**3)*100 - spotRadius
    drawArray.ellipse((xEnd, yEnd, xStart, yStart), fill=dotGrid[3])
    output.write(printSpot(SlideNo, dotGrid[1], dotGrid[2])) 
    global tiemp
    tiemp.append((dotGrid[0],dotGrid[1], dotGrid[2], xStart, yStart, RowSpacing, spotRadius)) 
    return 



# plot the array
for slide in slides:
	for i,sample in enumerate(samples):
                #first wash for every new sample
                output.write(wash*NbrWashes)
                output.write(FinalWash)
		#initialize variables for frequency of washing and no of spots at a time
		spots = 1
                totalSpots = 1
		 #get all spots in array with the same sample

		output.write(getSample(i, samples[i][2], samples[i][1]))
		for singlearray in arrays:
	                samplePos = [select for select in arrayGrid if sample[0] in select]
	                samplePos = [list(element) for element in samplePos]
                        samplePos = arrayShift(samplePos, singlearray)
                        #print "selected", sample[0], ":::", samplePos
			#print "samples >>>>>>>>>>>>>>>>>>>", samples
                       #take sample from Well and brag about it

                        output.write(sampleComment(samplePos[0][0], plateRowNames[samplePos[0][5]-1]+str(samplePos[0][4]), len(samplePos), singlearray))

                        for dot in range(0, len(samplePos)):
                                        if totalSpots < WashFreq:
                                                if spots < PrintSpots:
                                                        plotDot(samplePos[dot])
                                                        spots=spots+1
                                                        totalSpots=totalSpots+1
                                                else:
                                                        plotDot(samplePos[dot])
                                                        output.write(getSample(i, samplePos[dot][4], samplePos[dot][5]))
                                                        spots = 1
                                                        totalSpots = totalSpots+1
                                        else:
                                                plotDot(samplePos[dot])
                                                output.write(wash*NbrWashes)
                                                output.write(FinalWash)
                                                output.write(getSample(i, samplePos[dot][4], samplePos[dot][5]))
                                                totalSpots = 1

        
#        print len(samplePos)
#for dot in range(0, len(arrayGrid)):
 #   plotDot(arrayGrid[dot])

print tiemp[0:10]

output.write(footer)

plate.save("plate.png")
array.save("array.png")
