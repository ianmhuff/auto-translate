This script should hopefully make the process of translating SSBU status scripts a little less tedious by automatically performing many of the more basic steps, allowing you to focus on just cleaning up the logic.

The script will also keep code on the same line it started on; i.e. if a particular bit of code is on line 57 in the original, it will still be on line 57 when the script is done. That way, any lines of code that need additional work can be easily investigated by comparing against the original code.

I'm not a Python expert by any means so this code is probably insanely inefficient, but it works for now at the very least.

How to use:

Place auto-translate.py in the same directory as the files containing the scripts to be translated.

==== CAUTION ====

The script will indiscriminately and irrevocably modify any files it finds in the directory it is run in. I might add some kind of safety/guardrails later but for now there is nothing.

I have literally only tested it in a directory which contains the auto-translate.py and a copy of a fresh status script and nothing else. You have been warned.
