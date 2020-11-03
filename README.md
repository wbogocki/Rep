# Rep

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Rep is a tiny tool for freelancers and contractors to track time and calculate invoices. I wrote it to simplify my process and will continue to refine it along the way.

At the moment, Rep can:

- Track time
- Take notes
- Calculate invoices

## Approach

Rep uses logs to track your time and group notes. It's a very simple approach that I used to use with pen and paper.

For example, this is a single log:

```
Nov 4 2020 14:00 - Start work
Nov 4 2020 18:00 - Note: Let's go, wohoooooo!
Nov 5 2020 00:30 - Stop work
```

Rep stores these logs inside a hidden `.rep` directory in your project folder. The database is a human-friendly JSON file that can be edited when needed.

## Usage

There are six commands you need to know to use Rep:

| Command       | Action                                         |
| ------------- | ---------------------------------------------- |
| `rep init`    | Initialize Rep in the current directory.       |
| `rep start`   | Open a new log and start measuring time.       |
| `rep stop`    | Close the current log and stop measuring time. |
| `rep note`    | Add a note to the last log.                    |
| `rep table`   | Print logs in a table (doesn't show notes).    |
| `rep print`   | Print logs and notes.                          |
| `rep invoice` | Print the invoice amount for unbilled logs.    |
| `rep bill`    | Mark logs as billed.                           |

## License

Rep is licensed under the MIT license.
