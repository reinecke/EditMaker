EditMaster
==========

Python Editorial Tools

Right now the only useful thing is the Timecode object. This allows for simple
timecode math operations.

All calculations are made based on the total number of frames represented by
the timecode object.

So if you had a timecode of:
`00:00:01:00` @ 24fps (one second at 24 frames per second) - 24 total frames

and you added this timecode:
`00:00:02:00` @ 16fps (two seconds at 16 frames per second) - 32 total frames

it would yield:
`00:00:02:08` @ 24fps (two seconds and 8 frames at 24 frames per second) - 56 total frames

Examples
--------
    >>> # Instantiate a timecode object
    >>> tc1 = EditMaster.Timecode('01:00:03:12', fps=24)
    >>> tc1
    EditMaster.Timecode('01:00:03:12', fps=24)
    
    >>> # Access individual timecode components
    >>> tc1.hours
    1
    >>> tc1.minutes
    0
    >>> tc1.seconds
    3
    >>> tc1.frames
    12
    >>> tc1.total_frames
    86484
    >>> tc1.timecode
    '01:00:03:12'
    >>> tc1.seconds = 2
    >>> tc1
    EditMaster.Timecode('01:00:02:12', fps=24)
    
    >>> # Do math with the timecode
    >>> tc2 = EditMaster.Timecode('00:00:00:20', fps=24)
    >>> tc1 + tc2
    EditMaster.Timecode('01:00:04:08', fps=24)
    >>> tc1 - tc2
    EditMaster.Timecode('01:00:02:16', fps=24)
    >>> tc2 * 2
    EditMaster.Timecode('00:00:01:16', fps=24)
