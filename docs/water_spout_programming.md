### Water Spout Programming Language

The water spout programming language is used to control the water spouts. 

The machine uses one program at a time to make a water spout show.  The program
consists of one-line statements that are executed from top to bottom of the file,
with some statements causing the execution to return to labeled lines.  The program
quits (and all spouts are turned off) once the last statement of the file is executed.

The programming language does not use subroutines.  Rudimentary variables are
allowed -- but only containing integers.  Variables can be incremented or decremented.

The syntax of each statement is as follows:

command  arg1  arg2 ... argN  

where the number of arguments are different for each command.  

All uppercase is converted to lowercase on input -- therefore, case does not matter.

Lines that begin with the hashtag (#) are treated as comments and are ignored.  Blank
lines are ignored.  And characters following a hashtag, and the hashtag itself are ignored.

The parser does not issue errors.  Errors are ignored. Lines with errors are ignored or
executed with unexpected and unpredictable results.

Variables are donated by a star, such as "*i".  The name of the variable follows the star, and
can be any sequence of characters a-z and digits 0-9, and the usual special characters (_$).

Currently the following variables are global and are used as defaults for other commands.  In
addition these variables can be changed by the user while a program is running:

    *duration   -- usually controls the duration of a squirt.  Measured in milliseconds.
    *period     -- usually controls the pause between actions. Measured in milliseconds.
    *flow       -- usually controls the ball valve which regulates the flow of water. Measured in percent on.

Note: if the program sets a global variable its value will be displayed to the user on a web page refresh.

Note2: *flow cannot be set with the set statement. Use set-flow or change-flow statements to indirectly set
the *flow value. *flow reflects the actual position on of the ball valve and so may not be instantaneously updated or
match exactly the value commanded by the set-flow or change-flow statements.

Non global variables can be invented by the programmer as necessary.

## Program Commands

    name "string"               -- Gives the name of the program to be displayed in the UI.  If the name 
                                   has spaces, it must be enclosed with quotes.  The last name encountered
                                   will be used. If no name is given, then the name of the file will be used.

    set *var value              -- Sets a variable to a value.  The value can be a literal integer
                                   or another variable.

    inc *var [value]            -- Increments a variable.  The default increment is one.  An optional value
                                   can be used to set the increment value.

    dec *var [value]            -- decrement a variable.  The default decrement one. An optional value
                                   can be used to set the decrement value.

    all-off                     -- Turns all the water-spouts off.

    set-flow value              -- Sets the flow to a value.  Blocks until the flow is reached. (See notes below)

    change-flow value           -- Sets the flow to a value, but does not block while the flow is being changed.

    label label-name            -- Sets a flow control point in the program with the given label name.

    goto label-name             -- Changes the current execution line to the one with the given label.  If 
                                   label-name does not exist, flow continues to the next line without an error.

    if-zero *var label-name     -- Changes the current execution line to the one with the given label if the
                                   given variable is zero. If the variable does not exist, it is assumed to be zero.
                                   If the label-name does not exist, flow continues to the next line without an error.

    if-not-zero *var label-name -- Works like if-zero, except tests for non-zero.

    pause [value]               -- Pauses the number of milliseconds given by the value.  The value can be a
                                   variable or a literal integer.  If the value is not provided, then the global 
                                   variable *period is used.

    spout-on spout-name         -- Turns a spout or a group of spouts on.  The spout-name can be a litterial 
                                   (see below) or a variable. 

    spout-off spout-name        -- Turns a spout or a group of spouts off.  The spout-name can be a litterial
                                   (see below) or a variable. 

    squirt spout-name [d]       -- Causes a spout or group of spouts to squirt for a duration given by d. The
                                   duration is optional, and if not given then the global *duration is used.
                                   The program will block for the duration.

    random *var [i0 i1]         -- Sets the given variable to a random number between (and including) i0 and i1.
                                   If i0 and i1 are not given, then the random number will be between 0 and 13.

    hold                        -- Causes the program to hold in place and not advance. Basically puts the program
                                   into an infinite loop.

    exit                        -- Causes the program to quit and exit. All spouts are turned off.  Note that the
                                   program will automatically exit if there are no more statements to execute.

## Spout Names

The splash pad consists of 14 channels.  The first 13 channels control one water-spout each located in the middle of
the field.  These spouts are numbered from 0 to 12.  The 14th channel (number 13) controls five water-spouts by the gate. 
That is, all five water-spouts by the gate act in unison.

The channels are designed with the letters A-N.  The channels can also be designed with the numbers 0-13.  Therefore
the command "spout-on A" is equivalent to "spout-on 0".  Also, if, say, a varible named *x is zero, then the command
"spout-on *x" would also be equivalent.  T

In addition, group names for the spouts can be used with spout-on, spout-off, and squirt.  These names and corresponding indexes
are as follows:

        14  gate            -- The water-spouts by the gate
        15  center          -- The center spout
        16  corners         -- The spouts on the outside corners
        17  inside_corners  -- The spouts on the corners that form the inside box
        18  major_row_1     -- The major row closes to the gate
        19  major_row_2     -- The major row that includes the center
        20  major_row_3     -- The major row furthest from the gate
        21  minor_row_1     -- The minor row of the inside box, closes to the gate
        22  minor_row_2     -- The minor row of the inside box, farthest from the gate
        23  major_column_1  -- The major column on the west side
        24  major_column_2  -- The major column in the center
        25  major_column_3  -- The major column on the east side
        26  minor_column_1  -- the minor column of the inside box, on the west side
        27  minor_column_2  -- the minor column of the inside box, on the east side
        28  diagonal_1      -- the NW to SE diagonal
        29  diagonal_2      -- the NE to SW diagonal
        30  outside_box     -- the 8 spouts that forms the outside box
        31  inside_box      -- the 4 spouts that forms the inside box

Spout groups with ending numbers can be referred to as follows:
     
     spout-group-name[value]

where 'value' can be a variable or a literal value.  For example, minor_row[2] is the same as minor_row_2.

** Pad Layout

The water-spouts in the pad are laid out in the following pattern:


          WALL ============|             Gate             |============ WALL

                               N     N     N     N     N

                          A                B                 C

                                  D                E

                          F                G                 H

                                  I                J

                          K                L                 M

## Errors

As stated above, the parser has no facility for indicating errors, so errors are ignored.  In particular, any
line that has an unknown command is ignored.  Any non-existent or uninitialized variable is treated as zero. 
If a non-existent label in an if statement or a goto statement is designated, then control falls through to the
next line.  If a water-spout name is unknown, or out-of-bounds, then the statement is ignored.  Flow values are
limited to values between 0 and 100, and if out-of-bounds, then the flow value is capped.

## Program Operation

All program files are named in the form as "name.wsp" where "wsp" stands for "water spout program".  The name is invented by
the programmer.  The files are stored under the folder "wsp_scripts".  At startup, all files with the ".wsp" extension
are read in and made available for the user to run.  Currently, the website must be restarted to reload the files.

## More about Flow Control

The water flow for the entire system is controlled by one ball valve.  It takes about 5.3 seconds to fully open the
valve from the closed position or vice-versa.  In addition, there are two switches on the valve to detect the fully open
position and the fully closed position.  Moving from a fully open or closed position to an intermediary position 
is done by measuring elapsed time.  However, there is some backlash and coasting of the motor that is hard to predict
so the final position of the valve is slightly different from the commanded position. The position error gets worse
if the flow is changed from an intermediate position to another intermediate position. 

Therefore, it is best to move the valve to a fully open or closed position before moving to an intermediate position.
This can be done with commands "set-flow 0" or "set-flow 100", as these commands do not depend on timing, but rather these
use the switches to know when the command completes.

## Example Program

Here is an example program that fires the waterspouts randomly.  The user can use the UI to vary the duration and 
period between shots.

        # Random Program
        name Random
        set-flow 0 
        set-flow 30 
        label top 
        random *i 0 13
        spout-on *i 
        pause *duration 
        spout-off *i 
        pause *period 
        goto top 











