# spopy
Python script to generate xml configuration files for SpotBot 3  
The default SpocleGen program coming with ArrayIt SpotBot 3 array printer is pretty limited in selections (samples cannot be loaded from random plate positions or spotted in custom configurations (for example to control for spatial variation sin signal)
This small python script takes information from a plate and an array configuration in csv files and generates the necessary xml file (with .spo extension) necessary to do the SpotBot run. The script also produces simulated images of the plate and array to help with guidance.
The script has been used repeatedly in generating custom arrays but it's in no way a piece of proffesional software (I have no formal programming training, so, please be lenient)
