:information_source: Command `in`
Sends a reminder **__in__** some amount of time

Syntax to use: `in <expression>, <reminder>`

Examples:
`in 8h, wake up`, sends `wake up` in 8 hours
`in 7w, run backups` sends `run backups` in 7 weeks
`in 2d 3h 5m, look out` sends `look out` in 2 days, 3 hours and 5 minutes

Use `M` or `n` for months, `w` for weeks, `d` for days and `m` for minutes.  
Make sure to always include at least one time indicator, and do not forget the comma between time indicators and the reminder text!

You can make a reminder recurrent by adding an `every` like this:
`in 8h every 1d, wake up`
In this example, this reminder will come back everyday at the same time.