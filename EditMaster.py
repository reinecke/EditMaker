#!/usr/bin/env python
################################################################################
#   Name:       EditMaster
#   Description:
#       		Library for dealing with editorial information
#   History:    2010-06-10 - Initial creation
#   License: MIT
################################################################################
#The MIT License (MIT)
#
#Copyright (c) 2010 Eric Reinecke
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
import datetime

__doc__ = '''Library for managing edit info'''

class TimecodeArithmeticException(Exception):
    '''
    Exception raised when unsupported types are used to make calculations.
    e.x.
    tc = Timecode('00:43:12:02')
    tc * 'Apples!'
    ^ Not correct!
    '''

class Timecode(object):
    '''
    Object representing a specific timecode.
    Note: Drop-Frame timecode IS NOT SUPPORTED YET

    examples:
    tc = EditMaster.Timecode('00:00:01:04', fps=24)

    This object is geared to always preserve the total number of frames when
    performing operations. This means if you change fps, the hours, minutes,
    seconds, and frames values will change, but totalFrames will stay the same.

    Any operation setting minutes, seconds, or frames over 60, 60, and the fps
    respectively will cause an influence on the next most significant
    demomination. So if you start with a timecode 00:00:05:04 and you set the
    minutes to 70, the resulting timecode would be 01:60:05:04.
    Otherwise when you set any given field, it should not influence any other
    field.
    '''
    # Accessors
    def _getFrames(self):
        '''
        returns the frames portion of the timecode
        '''
        fpm = self.fps*60
        fph = fpm*60
        
        rates = [fph, fpm, self.fps]
        frames =  self._getComponent(rates)[1]

        return frames
    
    def _setFrames(self, frames):
        '''
        Sets the frames portion of the timecode
        '''
        newFrames = self.totalFrames - self.frames
        newFrames += frames
        self.totalFrames = newFrames
    
    def _getSeconds(self):
        '''
        returns the seconds portion of the timecode
        '''
        fpm = self.fps*60
        fph = fpm*60
        
        rates = [fph, fpm, self.fps]
        seconds = self._getComponent(rates)[0]
        
        return seconds
    
    def _setSeconds(self, seconds):
        '''
        sets the seconds portion of the timecode
        '''
        oldSeconds = self.seconds * self.fps
        newSeconds = seconds * self.fps
        self.totalFrames = self.totalFrames - oldSeconds + newSeconds
    
    def _getMinutes(self):
        '''
        returns the minutes portion of the timecode
        '''
        fpm = self.fps*60
        fph = fpm*60
        
        rates = [fph, fpm]
        minutes = self._getComponent(rates)[0]

        return minutes
    
    def _setMinutes(self, minutes):
        '''
        sets the minutes portion of the timecode
        '''
        fpm = self.fps*60

        oldMinutes = self.minutes * fpm
        newMinutes = minutes * fpm
        self.totalFrames = self.totalFrames - oldMinutes + newMinutes
    
    def _getHours(self):
        '''
        returns the minutes portion of the timecode
        '''
        fpm = self.fps*60
        fph = fpm*60
        
        rates = [fph]
        hours = self._getComponent(rates)[0]

        return hours
    
    def _setHours(self, hours):
        '''
        sets the minutes portion of the timecode
        '''
        fpm = self.fps*60
        fph = fpm*60

        oldHours = self.hours * fph
        newHours = hours * fph
        self.totalFrames = self.totalFrames - oldHours + newHours
    
    def _getTimecode(self):
        '''
        Returns the string timecode
        '''
        fmt = '%02d:%02d:%02d:%02d'
        
        return fmt % (self.hours, self.minutes, self.seconds, self.frames)
    
    def _setTimecode(self, timecode):
        '''
        Sets to the string timecode. This should be formatted as:
        HH:MM:SS:FF
        If this string has fewer than 4 fields, they will interpreted right to
        left, populating frames first
        '''
        self.totalFrames = _timecodeToFrames(timecode)

    # Properties
    frames = property(_getFrames, _setFrames,
                    doc = 'Represents the frames portion of the timecode')
    hours = property(_getHours, _setHours,
                    doc = 'Represents the hours portion of the timecode')
    minutes = property(_getMinutes, _setMinutes,
                    doc = 'Represents the minutes portion of the timecode')
    seconds = property(_getSeconds, _setSeconds,
                    doc = 'Represents the seconds portion of the timecode')
    timecode = property(_getTimecode, _setTimecode,
                    doc = 'Represents the timecode string')
    # Methods
    def __init__(self, timecode = "01:00:00:00", fps = 24, totalFrames = None):
        '''
        Constructor for creating a timecode object.
        Defaults to a timecode of one hour at 24fps

        Inputs:
        ------------------------------------------------------------------------
        timecode    - A string representation of a given timecode as HH:MM:SS:FF
        fps         - Frames per second to represent the timecode in
        frames      - A frame number. At 24 fps frame 1010 is equal to
                      a timecode of '00:00:42:02' If this is specified it will
                      override timecode argument
        '''
        # Internal storage
        self.fps = fps

        if totalFrames:
            self.totalFrames = totalFrames
        else:
            self.totalFrames = self._timecodeToFrames(timecode)
    
    def __repr__(self):
        return "EditMaster.Timecode('%s', fps=%d)" % (self.timecode, self.fps)

    def __str__(self):
        return '<EditMaster.Timecode: %s @ %d fps>' %(self.timecode, self.fps)


    def _getComponent(self, baseList):
        '''
        Whittles down totalFrames by each base. Returns a tuple of the evenly
        divisible number for the last base in the list and leftover frames.
        i.e. pass a list like [fph, fpm, fps] and you will get the seconds
        portion of the timecode, pass [fph, fpm] and you will get the minutes.
        '''
        leftoverFrames = self.totalFrames
        amount = None
        for base in baseList:
            amount = leftoverFrames // base
            leftoverFrames = leftoverFrames % base

        return (amount, leftoverFrames)

    def _timecodeToFrames(self, timecode, fps=None):
        '''
        Converts the given timecode string to integer frames.

        Inputs:
        ------------------------------------------------------------------------
        timecode    - HH:MM:SS:FF formatted string representing timecode. If
                      this string has fewer than 4 fields, they will be
                      interpreted as the least significant first.
                      e.g. '04:03:22' will be 4 minutes, 3 seconds, 22 frames
        fps         - Number of frames per second, defaults to self.fps
        '''
        if not fps:
            fps = self.fps
        # Calculate frame rates in hour and minute bases
        fpm = fps*60
        fph = fpm*60
        
        multipliers = [1, fps, fpm, fph]
        frames = 0
        tcElements = timecode.split(':')
        tcElements.reverse()
        for i,element in enumerate(tcElements):
            multiplier = multipliers[i]
            frames += int(element)*multiplier

        return frames
    
    # Operators
    def _opDetermineFrames(self, something):
        '''
        Tries to determine a sane frame representation of the type handed in
        '''
        thingType = type(something)
        if thingType == str:
            return self._timecodeToFrames(something)
        if thingType == int or thingType == float:
            return something
        if thingType == Timecode:
            return something.totalFrames
        
        raise TimecodeArithmeticException(
            "Could not convert operand to a Timecode compatible type")

    def __add__(self, other):
        newTotalFrames = self.totalFrames + self._opDetermineFrames(other)
        return Timecode(fps = self.fps, totalFrames = newTotalFrames)

    def __sub__(self, other):
        newTotalFrames = self.totalFrames - self._opDetermineFrames(other)
        return Timecode(fps = self.fps, totalFrames = newTotalFrames)
    
    def __mul__(self, other):
        otherType = type(other)
        if otherType == float or otherType == int:
            newTotalFrames = self.totalFrames * other
            return Timecode(fps = self.fps, totalFrames = newTotalFrames)
        else:
            raise TimecodeArithmeticException(
            "Could not convert operand to a Timecode compatible type")
    
    def __div__(self, other):
        otherFrames = self._opDetermineFrames(other)
        divFrames = self.totalFrames // otherFrames
        if type(other) == Timecode:
            return int(divFrames)
        else:
            return Timecode(totalFrames = int(divFrames), fps = self.fps)

    def __mod__(self, other):
        if type(other) != Timecode:
            raise TimecodeArithmeticException(
            "Could not convert operand to a Timecode compatible type")
        otherFrames = self._opDetermineFrames(other)
        remainingFrames = self.totalFrames % otherFrames
        return Timecode(totalFrames = remainingFrames, fps = self.fps)
    
    def __lt__(self, other):
        if type(other) != Timecode:
            raise TimecodeArithmeticException(
            "Could not convert operand to a Timecode compatible type")
        return self.totalFrames < other.totalFrames

    def __le__(self, other):
        if type(other) != Timecode:
            raise TimecodeArithmeticException(
            "Could not convert operand to a Timecode compatible type")
        return self.totalFrames <= other.totalFrames

    def __eq__(self, other):
        if type(other) != Timecode:
            raise TimecodeArithmeticException(
            "Could not convert operand to a Timecode compatible type")
        return self.totalFrames == other.totalFrames

    def __ne__(self, other):
        if type(other) != Timecode:
            raise TimecodeArithmeticException(
            "Could not convert operand to a Timecode compatible type")
        return self.totalFrames != other.totalFrames

    def __gt__(self, other):
        if type(other) != Timecode:
            raise TimecodeArithmeticException(
            "Could not convert operand to a Timecode compatible type")
        return self.totalFrames > other.totalFrames

    def __ge__(self, other):
        if type(other) != Timecode:
            raise TimecodeArithmeticException(
            "Could not convert operand to a Timecode compatible type")
        return self.totalFrames >= other.totalFrames

class editEvent(object):
    '''
    represents an editorial event.
    '''
    def __init__(self, start = Timecode(), end = Timecode()):
        self.eventName = None
        self.tracks = 'VA1A2'
        self.start = Timecode()
        self.end = Timecode()
        self.markIn = Timecode()
        self.markOut = Timecode()
        self.tape = None
        self.scene = None
        self.DPX = None
        self.comment = None
        self.creationDate = datetime.datetime.now()

