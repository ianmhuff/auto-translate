This script should hopefully make the process of translating SSBU status scripts a little less tedious by automatically performing many of the more basic steps, allowing you to focus on just cleaning up the logic.

The script will also keep code on the same line it started on; i.e. if a particular bit of code is on line 57 in the original, it will still be on line 57 when the script is done. That way, any lines of code that need additional work can be easily investigated by comparing against the original code.

I also left in the tilde lines as comments reformatted as ```free(var)``` since I sometimes find them helpful for following the logic of the script.

I'm not a Python expert by any means so this code is probably pretty inefficient, but it works for now at the very least.

How to use:

Place auto-translate.py in the same directory as the files containing the scripts to be translated.

==== CAUTION ====

The script will (should) indiscriminately and irrevocably modify any files it finds in the directory it is run in. I might add some kind of safety/guardrails later but for now there is nothing. I also make no guarantees that there isn't something, like, horribly wrong with the implementation of searching for files.

I have literally only tested it on one computer, in a directory which contains auto-translate.py, a copy of a fresh status script, and nothing else. Run it at your own peril and all that.
