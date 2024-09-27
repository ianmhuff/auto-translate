This script should hopefully make the process of translating SSBU status scripts a little less tedious by automatically performing many of the more basic steps, allowing you to focus on just cleaning up the logic.

The script will also keep line numbers intact; i.e. if a particular bit of code is on like 57 in the original, it will still be on line 57 when the script is done. That way, any lines of code that need additional work can be easily investigated by comparing against the original code.

How to use:

Place auto-translate.py in the same directory as the files containing the scripts to be translated.

==== CAUTION ====

The script will indiscriminately and irrevocably modify any files it finds in its directory. I will probably add some "safety" guardrails later but for now there is nothing.

I have literally only tested it in a directory which contains the auto-translate.py and a copy of a fresh status script and nothing else. You have been warned.
