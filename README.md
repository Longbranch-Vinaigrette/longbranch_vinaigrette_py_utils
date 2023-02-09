# Devtools Utils

Utility functions and class for the devtools stack.

# Requirements

Other submodules required:
* sub.process-utils
* sub.sqlite3-utils

Note that this submodules must be placed on the SAME LEVEL as this one, renamed like this:
* sub.process_utils = process_utils
* sub.sqlite3-utils = sqlite3_utils

Because some functionality uses those submodules by importing them relatively
using 'from .. import process_utils'

SAME LEVEL:
The same level are files/folder literally located on the same folder.
For example:
\submodules
| \dev_tools_utils 
| \sqlite3_utils    <-- Is on the same level as 'dev_tools_utils'
