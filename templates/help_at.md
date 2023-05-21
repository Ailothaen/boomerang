:information_source: Command `at`/`on`
Sends a reminder **__at__** a particular time

Syntax to use: `at <expression>, <reminder>` (`at` may be replaced by `on`)

Several formats are accepted, here are some examples:
`at 8, wake up` sends `wake up` at 8:00 (AM)
`at 19:00, water flowers` sends `water flowers` at 19:00 (7:00 PM)
`on 6, make backups` sends `make backups` on the 6th of the month (at midnight)
`on 15 at 12h, lunch outside` sends `lunch outside` on the 15th of month at noon

You can make a reminder recurrent by adding an `every` like this:
`at 8 every 1d, wake up`
In this example, this reminder will come back everyday at 8:00.