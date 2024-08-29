### Final Notes and Thoughs as of Aug 2024

These notes after two weeks of working on the Splash Pad and finishing up before going on vacation with Carol.

1. The Website needs to be an appliation with instantaneous updates.  Currently the status displayed at the top of the main page
is always stale, and leads to confusion.  The website should be writen as a javascript app, and ask for constant updates.

2. The operation of the solenoids are inconsistant from one another.  Some get stuck more than others which leads to delays in 
the squirt and/or the squirt not being the same height.

3. Do to the variation in the solenoids, the length of pipe to each spout, and other unknown factors, the spouts are not
consistant with each other, and probably will never be, at least without a completely new design to control each channel.

4. The PSI sensors do not work.  The first seemed like it was working for the first few days, but the second always has read low.
Now, neither seems to be giving the correct readings.  Also, there are errors reported from the Pi Pico and the Rasberry Pi for the
serial line.  This should never happen.?

5. Controlling the overall flow is teriable.  Better status updates might help.  Also I am not sure if the change-flow wsp command
works correctly.  Again, a beter status output would help in debugging.

6. The web page needs to be more responsive.  Buttons should click.  More feedback as to what is happening (which program is running, if any)

7. The web site should provide a log which shows errors in the program.

8. The web site should have a way to create, edit, and delete the water spout scripts.  

9. The master solenoid should be under program control.  Then power could be applied 24/7 and the Raspberry Pi could use timeouts to
keep the master solenoid from getting to hot, and shut down slow leaks when the system is not being used.


Even with all the above problems, this version of the Splash Pad is fully usable and fun.  Not sure how much added enjoyment will be goten
by fixing these problems.  

For an ultimate Splash Pad, work needs to be done to design a squirter that controls volumn, height, timing, and flow.  It should have a way
to perfectly command a shot of water to a specific height for a specific time period.  It needs to take into account the volumn (and therefore weight)
of the water in the pipe from the point of control to the point of release.  Once such a machine is invented, then a custom circut board needs
to be designed to put the machine under computer control.  And the machine needs 14 identical channels, and has to fit in the vault, and have
a way to be maintained.  (3-6 man months?)

