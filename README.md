# stl-waterline
Simulate STL boat hull floating

I designed a hull in onshape and wanted to figure out more or less where the waterline would be and what it would look like floating.  I didn't see an existing tool that could do this for free, so I made this little script.  It's kinda hacky but it makes nice animations.

![](https://github.com/stl-waterline/rear.gif)

![](https://github.com/stl-waterline/side.gif)

There are two big assumptions:

 - this is only vaguely accurate for small angles away from equilibrium.  if the hull gets too far then things get crazy and the hull yeets off the "water" in unrealist ways
 
 - the hull's weight must be somewhat realistic.  otherwise small errors in the initial draft will get amplified and once again yeet the hull into the ether.

Also, the simulation should work for any hull STL, but the rendering is very naive and only looks right when the hull is a solid object.